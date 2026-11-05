#!/usr/bin/env bash
set -euo pipefail

CLUSTER=ctf-tickets
CONTEXT=kind-$CLUSTER
IMAGE=p4ck3t0/tickets:latest
DIR=$(dirname "$0")

if grep -qx "$CLUSTER" <<<"$(kind get clusters 2>/dev/null)"; then
  echo "error: kind cluster \"$CLUSTER\" already exists, delete it first with: kind delete cluster --name $CLUSTER" >&2
  exit 1
fi

kind create cluster --name "$CLUSTER"

if docker image inspect "$IMAGE" >/dev/null 2>&1; then
  kind load docker-image "$IMAGE" --name "$CLUSTER"
else
  echo "note: $IMAGE not found locally; relying on the registry. Build it with ./build.sh" >&2
fi

kubectl --context "$CONTEXT" apply --server-side -f "$DIR/challenge.yaml" || true
kubectl --context "$CONTEXT" wait --for=condition=established crd/challenges.fluxfingers.ctf --timeout=60s
kubectl --context "$CONTEXT" apply --server-side -f "$DIR/challenge.yaml"
kubectl --context "$CONTEXT" apply -f "$DIR/user.yaml"

for d in controller api ui web-templates misc-templates crypto-templates pwn-templates rev-templates; do
  kubectl --context "$CONTEXT" -n ctf rollout status "deployment/$d" --timeout=5m
done

server=$(kubectl config view --raw --minify --context "$CONTEXT" -o jsonpath='{.clusters[0].cluster.server}')
ca=$(kubectl config view --raw --minify --context "$CONTEXT" -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')
token=$(kubectl --context "$CONTEXT" -n ctf create token ctf-player --duration=8760h)

cat > ctf-player.kubeconfig <<KUBECONFIG
apiVersion: v1
kind: Config
clusters:
- name: $CLUSTER
  cluster:
    server: $server
    certificate-authority-data: $ca
users:
- name: ctf-player
  user:
    token: $token
contexts:
- name: ctf-player
  context:
    cluster: $CLUSTER
    user: ctf-player
    namespace: ctf
current-context: ctf-player
KUBECONFIG

echo
echo "challenge tracker is up. kubeconfig for ctf-player written to $PWD/ctf-player.kubeconfig"
echo "  export KUBECONFIG=$PWD/ctf-player.kubeconfig"
echo "reach the UI (the only thing the player may do) with:"
echo "  kubectl port-forward svc/ui 8080:80"
echo "then open http://localhost:8080"
echo "tear down with: kind delete cluster --name $CLUSTER"
