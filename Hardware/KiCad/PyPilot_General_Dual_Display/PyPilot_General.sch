EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "PyPilot General "
Date "2021-05-18"
Rev "1.0"
Comp "SV SuAn"
Comment1 "Lutz J. Pestel"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
NoConn ~ 2050 4800
Wire Wire Line
	800  4600 800  4850
Wire Wire Line
	1600 5400 800  5400
Wire Wire Line
	800  5400 800  5350
Wire Wire Line
	2050 4700 1600 4700
Wire Wire Line
	1600 4700 1600 5400
$Comp
L power:+12V #PWR09
U 1 1 60A7605E
P 5300 3000
F 0 "#PWR09" H 5300 2850 50  0001 C CNN
F 1 "+12V" H 5315 3173 50  0000 C CNN
F 2 "" H 5300 3000 50  0001 C CNN
F 3 "" H 5300 3000 50  0001 C CNN
	1    5300 3000
	1    0    0    1   
$EndComp
$Comp
L power:GND #PWR04
U 1 1 60A3C384
P 1950 4500
F 0 "#PWR04" H 1950 4250 50  0001 C CNN
F 1 "GND" V 1955 4372 50  0000 R CNN
F 2 "" H 1950 4500 50  0001 C CNN
F 3 "" H 1950 4500 50  0001 C CNN
	1    1950 4500
	0    1    1    0   
$EndComp
Wire Wire Line
	5100 3000 5300 3000
Wire Wire Line
	5100 2900 5300 2900
$Comp
L power:+12V #PWR02
U 1 1 60A7597E
P 1950 4350
F 0 "#PWR02" H 1950 4200 50  0001 C CNN
F 1 "+12V" H 1965 4523 50  0000 C CNN
F 2 "" H 1950 4350 50  0001 C CNN
F 3 "" H 1950 4350 50  0001 C CNN
	1    1950 4350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR011
U 1 1 60A75980
P 5300 2900
F 0 "#PWR011" H 5300 2650 50  0001 C CNN
F 1 "GND" H 5305 2727 50  0000 C CNN
F 2 "" H 5300 2900 50  0001 C CNN
F 3 "" H 5300 2900 50  0001 C CNN
	1    5300 2900
	1    0    0    1   
$EndComp
Wire Wire Line
	2050 4400 1950 4400
Wire Wire Line
	1950 4400 1950 4350
Wire Wire Line
	2050 4500 1950 4500
Wire Wire Line
	800  4600 2050 4600
Connection ~ 5300 3000
Connection ~ 5300 2900
$Comp
L power:+12V #PWR08
U 1 1 60A7597C
P 5300 3000
F 0 "#PWR08" H 5300 2850 50  0001 C CNN
F 1 "+12V" H 5315 3173 50  0000 C CNN
F 2 "" H 5300 3000 50  0001 C CNN
F 3 "" H 5300 3000 50  0001 C CNN
	1    5300 3000
	1    0    0    1   
$EndComp
$Comp
L power:GND #PWR05
U 1 1 60A7597D
P 1950 4500
F 0 "#PWR05" H 1950 4250 50  0001 C CNN
F 1 "GND" V 1955 4372 50  0000 R CNN
F 2 "" H 1950 4500 50  0001 C CNN
F 3 "" H 1950 4500 50  0001 C CNN
	1    1950 4500
	0    1    1    0   
$EndComp
$Comp
L power:+12V #PWR01
U 1 1 60A3CBDC
P 1950 4350
F 0 "#PWR01" H 1950 4200 50  0001 C CNN
F 1 "+12V" H 1965 4523 50  0000 C CNN
F 2 "" H 1950 4350 50  0001 C CNN
F 3 "" H 1950 4350 50  0001 C CNN
	1    1950 4350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR010
U 1 1 60A3DC1D
P 5300 2900
F 0 "#PWR010" H 5300 2650 50  0001 C CNN
F 1 "GND" H 5305 2727 50  0000 C CNN
F 2 "" H 5300 2900 50  0001 C CNN
F 3 "" H 5300 2900 50  0001 C CNN
	1    5300 2900
	1    0    0    1   
$EndComp
$Comp
L Motor:Motor_DC M1
U 1 1 60A37F85
P 800 5050
F 0 "M1" H 958 5046 50  0000 L CNN
F 1 "Hydraulic Pump" H 958 4955 50  0000 L CNN
F 2 "" H 800 4960 50  0001 C CNN
F 3 "~" H 800 4960 50  0001 C CNN
	1    800  5050
	1    0    0    -1  
$EndComp
$Comp
L power:+12V #PWR07
U 1 1 60A3B846
P 5300 3000
F 0 "#PWR07" H 5300 2850 50  0001 C CNN
F 1 "+12V" H 5315 3173 50  0000 C CNN
F 2 "" H 5300 3000 50  0001 C CNN
F 3 "" H 5300 3000 50  0001 C CNN
	1    5300 3000
	1    0    0    1   
$EndComp
$Comp
L power:GND #PWR06
U 1 1 60A7605F
P 1950 4500
F 0 "#PWR06" H 1950 4250 50  0001 C CNN
F 1 "GND" V 1955 4372 50  0000 R CNN
F 2 "" H 1950 4500 50  0001 C CNN
F 3 "" H 1950 4500 50  0001 C CNN
	1    1950 4500
	0    1    1    0   
$EndComp
$Comp
L power:+12V #PWR03
U 1 1 60A76060
P 1950 4350
F 0 "#PWR03" H 1950 4200 50  0001 C CNN
F 1 "+12V" H 1965 4523 50  0000 C CNN
F 2 "" H 1950 4350 50  0001 C CNN
F 3 "" H 1950 4350 50  0001 C CNN
	1    1950 4350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR012
U 1 1 60A76062
P 5300 2900
F 0 "#PWR012" H 5300 2650 50  0001 C CNN
F 1 "GND" H 5305 2727 50  0000 C CNN
F 2 "" H 5300 2900 50  0001 C CNN
F 3 "" H 5300 2900 50  0001 C CNN
	1    5300 2900
	1    0    0    1   
$EndComp
$Comp
L PyPilot_General-rescue:PyPilot_Dual_Display-General_Library U6
U 1 1 60A3CEB7
P 9500 2500
F 0 "U6" H 9850 2450 50  0000 L CNN
F 1 "PyPilot_Dual_Display" H 9550 2350 50  0000 L CNN
F 2 "" H 9500 2500 50  0001 C CNN
F 3 "" H 9500 2500 50  0001 C CNN
	1    9500 2500
	1    0    0    -1  
$EndComp
Connection ~ 1950 4350
Connection ~ 1950 4500
$Comp
L PyPilot_General-rescue:StepDownRegulator12V-5V-General_Library U?
U 1 1 60AE5D46
P 8600 2950
F 0 "U?" H 8700 3225 50  0000 C CNN
F 1 "StepDownRegulator12V-5V" H 8700 3134 50  0000 C CNN
F 2 "" H 8600 2950 50  0001 C CNN
F 3 "" H 8600 2950 50  0001 C CNN
	1    8600 2950
	1    0    0    -1  
$EndComp
Wire Wire Line
	9050 2900 9300 2900
Wire Wire Line
	9050 3000 9300 3000
Wire Wire Line
	2850 3500 2850 3200
Wire Wire Line
	2300 3500 2850 3500
Wire Wire Line
	2950 3300 2950 3600
Wire Wire Line
	2300 3600 2950 3600
Wire Wire Line
	2950 3300 5550 3300
Wire Wire Line
	5550 3000 5300 3000
Wire Wire Line
	5550 2900 5300 2900
Text Notes 1000 3700 0    50   ~ 0
Robertson rudder angle \nfeedback sensor \n(Frequency Modulated)
Text Notes 4300 4100 0    50   ~ 0
Alternativ rudder feedback sensor.\n(0..5V) output
Text Notes 2250 5300 0    50   ~ 0
Motor Controller is part \nof the original\nOpen Source \nPyPilot Project.
Text Notes 5900 6200 0    50   ~ 0
Main purpose:\n1) Convert frequency modulated\nrudder angle feedback in 0-5V\nanalog signal and feed it to the \nMotor Controller (J5.2).\n2) Generate NMEA rudder angle\nsentence and feed it to the helm.
Text Notes 9350 4550 0    50   ~ 0
1) The PyPilot hard and software (original)\n2) Arduino with second display for displaying\nthe rudder angle.
Text Notes 2400 5700 0    50   ~ 0
This unit was bought \nready made from the \ncreator of PyPilot.
Wire Wire Line
	7775 3000 7775 2900
Wire Wire Line
	7775 2900 8350 2900
$Comp
L General:RF300_Interface U?
U 1 1 612C7A91
P 5850 2600
F 0 "U?" H 6550 2665 50  0000 C CNN
F 1 "RF300_Interface" H 6550 2574 50  0000 C CNN
F 2 "" H 5850 2600 50  0001 C CNN
F 3 "" H 5850 2600 50  0001 C CNN
	1    5850 2600
	1    0    0    -1  
$EndComp
Wire Wire Line
	7550 3000 7775 3000
Wire Wire Line
	2850 3200 5550 3200
$Comp
L Connector:Screw_Terminal_01x02 J1
U 1 1 60A3629E
P 4900 2900
F 0 "J1" H 4900 2600 50  0000 C CNN
F 1 "12V Power" H 4818 2666 50  0000 C CNN
F 2 "" H 4900 2900 50  0001 C CNN
F 3 "~" H 4900 2900 50  0001 C CNN
	1    4900 2900
	-1   0    0    -1  
$EndComp
$Comp
L General:RF300 U?
U 1 1 612CF7AB
P 2300 3300
F 0 "U?" H 1808 3465 50  0000 C CNN
F 1 "RF300" H 1808 3374 50  0000 C CNN
F 2 "" H 2300 3300 50  0001 C CNN
F 3 "" H 2300 3300 50  0001 C CNN
	1    2300 3300
	1    0    0    -1  
$EndComp
$Comp
L General:Hall_Angle_Sensor U?
U 1 1 612CFF53
P 5100 3350
F 0 "U?" H 5096 3439 50  0000 C CNN
F 1 "Hall_Angle_Sensor" H 5096 3348 50  0000 C CNN
F 2 "" H 5300 2950 50  0001 C CNN
F 3 "" H 5300 2950 50  0001 C CNN
	1    5100 3350
	1    0    0    -1  
$EndComp
Wire Wire Line
	5350 3550 5550 3550
Wire Wire Line
	5350 3650 5550 3650
Wire Wire Line
	5350 3750 5550 3750
$Comp
L General:Motor_Controller U?
U 1 1 612D193A
P 2750 4100
F 0 "U?" H 2850 4065 50  0000 C CNN
F 1 "Motor_Controller" H 2850 3974 50  0000 C CNN
F 2 "" H 2750 4100 50  0001 C CNN
F 3 "" H 2750 4100 50  0001 C CNN
	1    2750 4100
	1    0    0    -1  
$EndComp
Wire Wire Line
	3650 4450 4275 4450
Wire Wire Line
	4275 4450 4275 4400
Wire Wire Line
	4275 4400 5550 4400
Wire Wire Line
	3650 4550 4325 4550
Wire Wire Line
	4325 4550 4325 4500
Wire Wire Line
	4325 4500 5550 4500
Wire Wire Line
	3650 4650 4375 4650
Wire Wire Line
	4375 4650 4375 4600
Wire Wire Line
	4375 4600 5550 4600
Wire Wire Line
	3650 5200 4150 5200
Wire Wire Line
	4150 5200 4150 5300
Wire Wire Line
	4150 5300 5550 5300
Wire Wire Line
	3650 5100 4250 5100
Wire Wire Line
	4250 5100 4250 5200
Wire Wire Line
	4250 5200 5550 5200
Wire Wire Line
	3650 5000 4375 5000
Wire Wire Line
	4375 5000 4375 5100
Wire Wire Line
	4375 5100 5550 5100
Wire Wire Line
	3650 4900 4500 4900
Wire Wire Line
	4500 4900 4500 5000
Wire Wire Line
	4500 5000 5550 5000
Wire Wire Line
	9300 3600 8850 3600
Wire Wire Line
	8850 3600 8850 4800
Wire Wire Line
	8850 4800 7550 4800
Wire Wire Line
	9275 3700 8925 3700
Wire Wire Line
	8925 3700 8925 4700
Wire Wire Line
	8925 4700 7550 4700
Wire Wire Line
	7550 4300 8200 4300
Wire Wire Line
	8200 4300 8200 4100
Wire Wire Line
	8200 4100 9300 4100
Wire Wire Line
	7550 4400 8250 4400
Wire Wire Line
	8250 4400 8250 4000
Wire Wire Line
	8250 4000 9300 4000
Wire Wire Line
	8775 3500 8775 4900
Wire Wire Line
	8775 4900 7550 4900
Wire Wire Line
	8725 5000 8725 3400
Wire Wire Line
	7550 5000 8725 5000
Wire Wire Line
	9300 3500 8775 3500
Wire Wire Line
	8725 3400 9300 3400
Wire Wire Line
	8325 3900 9300 3900
Wire Wire Line
	8400 3800 9300 3800
Wire Wire Line
	7550 4500 8325 4500
Wire Wire Line
	8325 4500 8325 3900
Wire Wire Line
	7550 4600 8400 4600
Wire Wire Line
	8400 4600 8400 3800
Text Notes 7675 4300 0    50   ~ 0
brown
Text Notes 8950 4100 0    50   ~ 0
brown
Text Notes 7675 4400 0    50   ~ 0
brown-white
Text Notes 8950 4000 0    50   ~ 0
brown-white
Text Notes 7675 4600 0    50   ~ 0
blue
Text Notes 7675 4500 0    50   ~ 0
blue-white
Text Notes 8950 3900 0    50   ~ 0
blue-white
Text Notes 8950 3800 0    50   ~ 0
blue
Text Notes 7675 4700 0    50   ~ 0
orange
Text Notes 7675 4800 0    50   ~ 0
orange-white
Text Notes 7675 4900 0    50   ~ 0
green-white
Text Notes 7675 5000 0    50   ~ 0
green
Text Notes 8925 3375 0    50   ~ 0
green
Text Notes 8825 3500 0    50   ~ 0
green-white
Text Notes 8825 3600 0    50   ~ 0
orange-white
Text Notes 8900 3700 0    50   ~ 0
orange
$EndSCHEMATC
