<?php
    // if you receive the showSource parameter, display the source code
    if (isset($_GET['showSource'])) {
        show_source(__FILE__);
        exit();
    }

?>
<html>
<head>
    <title>Web Application Firewall</title>
</head>
<body>
    <!-- 
        The flag is in the file ../secrets/flag.txt 
        to view the source code, add the parameter showSource=true to the URL
    -->
    <p>Your objective is to read the contents of the file "../secrets/flag.txt".</p>
    <p>Enter the name of the file you want to view(empty or nothing):</p>
    <form method="post">
        <input type="text" name="fileName">
        <input type="submit" value="View">
    </form>
    <br>
    <p>File contents:</p>
    <p>
        <?php
            if (isset($_POST['fileName'])) {           
                $userInput = $_POST['fileName'];
                $indexesOfDirtyChars = [];
                for ($i = 0; $i < strlen($userInput); $i++) {
                    if ($userInput[$i] === ".") {
                        $indexesOfDirtyChars[] =$i;
                    }
                }
                if (count($indexesOfDirtyChars) > 0) {
                    echo "<p> Dirty file name $userInput chars at indexes: ";
                    for ($i = 0; $i < count($indexesOfDirtyChars); $i++) {
                        echo $indexesOfDirtyChars[$i];
                        if ($i < count($indexesOfDirtyChars) - 1) {
                            echo ", ";
                        }
                    }
                    echo "</p>";
                }
                $lowerFileName = mb_strtolower($userInput, 'UTF-8');
                $nRemoved = 0;
                $i = 0;
                $cleanFileName = "";
                for ($id = 0; $id < count($indexesOfDirtyChars); $id++) {
                    while($i < $indexesOfDirtyChars[$id]) {
                        $cleanFileName .= $lowerFileName[$i];
                        $i++;
                    }
                    $i++;
                }
                while($i < strlen($lowerFileName)) {
                    $cleanFileName .= $lowerFileName[$i];
                    $i++;
                }
                $finalName = "./static/".$cleanFileName;
                echo "<p>Reading file: $finalName</p>";
                $file = file_get_contents($finalName);
                echo "<p>$file</p>";

            }
        ?>

    </p>
</html>