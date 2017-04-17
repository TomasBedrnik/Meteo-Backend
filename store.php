<?php

#Don't forget to set your locale in php.ini
#you need to have write access to file dir (note /tmp with systemd sometimes does not work

$dir = "/home/beda/data/test/";
$out .= "\nphp://input:";
$out .= file_get_contents('php://input');

$data = json_decode(file_get_contents('php://input'), true);

if (count($data) == 0) {
#TEST run -> try to create file in dir
    $somecontent = "Test.";
    $filename = $dir."test.txt";
    if (!$handle = fopen($filename, 'w')) {
        echo "Cannot open file ($filename), script won't work!";
        exit;
    }

    if (fwrite($handle, $somecontent) === FALSE) {
        echo "Cannot write to file ($filename), script won't work!";
        exit;
    }
    
    if(unlink($filename) === FALSE) {
        echo "Cannot delete file ($filename), script probably won't work!";
        exit;
    }
    echo "Success, wrote ($somecontent) to file ($filename) and deleted it.";

    fclose($handle);
} else {
    if (array_key_exists('sensorType', $data)) {
        $out .= "\n sensorType:";
        $out .= $data["sensorType"];
        $out .= "\n timeSleep:";
        $out .= $data["timeSleep"];
        $out .= "\n";
        if ($data["sensorType"] == "Temperature" && array_key_exists('temperatures', $data)) {
            $out .= "Temperatures[";
            $out .= count($data["temperatures"]);
            $out .= "] : ";
            foreach ($data["temperatures"] as $val) {
                $out .= $val;
                $out .= "; ";
            }
            $out .= "\n";
        }
        if (array_key_exists('times', $data)) {
            $out .= "Times[";
            $out .= count($data["times"]);
            $out .= "] : ";
            foreach ($data["times"] as $val) {
                $out .= $val;
                $out .= "; ";
            }
            $out .= "\n";
        }
        $now = microtime(true);
        $out .= "Time: ";
        $micro = sprintf("%06d", ($now - floor($now)) * 1000000);
        $d = new DateTime(date('Y-m-d H:i:s.' . $micro, $now));
        $out .= $d->format("Y-m-d H:i:s.u"); // note at point on "u"
        $out .= "\n";

        //TODO: ADD length checks!!!
        $curT = $now;
        for ($i = count($data["temperatures"]) - 1; $i >= 0; $i--) {
            $out .= $data["temperatures"][$i];
            $out .= " | ";
            if ($i == count($data["temperatures"]) - 1) {
                $curT = $curT - ($data["times"][$i] / 1000);
            } else {
                $curT = $curT - $data["timeSleep"] - ($data["times"][$i] / 1000);
            }
            $micro = sprintf("%06d", ($curT - floor($curT)) * 1000000);
            $d = new DateTime(date('Y-m-d H:i:s.' . $micro, $curT));
            $out .= $d->format("Y-m-d H:i:s.u"); // note at point on "u"
            $out .= "\n";
        }
    }

    $handle = fopen($dir."test-PHP", 'a');
    fwrite($handle, $out);
    fclose($handle);
}