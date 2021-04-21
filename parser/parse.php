<?php


ini_set('display_errors', 'stderr');
setlocale(LC_ALL, 'cs_CZ.UTF-8');

const ZERO_PARAMETERS = 1;
const ONE_PARAMETER = 2;
const TWO_PARAMETERS = 3;
const THREE_PARAMETERS = 4;

const LOC = 0;
const COMMENTS = 1;
const LABELS = 2;
const JUMPS = 3;
const BACKJUMPS = 4;
const FWJUMPS = 5;
const BADJUMPS = 6;

// helping arrays for bonus task
$parameters = array_fill(0, 7, 0);   // main array for counting of variables
$jump_array = [];
$label_array = [];

arguments_check($argc, $argv); // checking arguments

//  -----------------------   M A I N   C O D E   -----------------------

// start working with xmlwriter
$xw = xmlwriter_open_memory();
xmlwriter_set_indent($xw, 1);
$res = xmlwriter_set_indent_string($xw, '    ');

xmlwriter_start_document($xw, '1.0', 'UTF-8');

$header_exists = false;

// start of syntax analyze
while($income_str = fgets(STDIN)){

    $arg_counter = 1;
    $income_array = noSpacesAndHashtag($income_str);
    
    // check if array is empty, check header
    if(empty($income_array) || $income_array[0] == NULL || $income_array[0] == '#' || $income_array[0] == '\n')
        continue;
    else if (!$header_exists){
        if(strtoupper($income_array[0]) == ".IPPCODE21\n" || strtoupper($income_array[0]) == ".IPPCODE21"){     //  ------------------------------ 2 1 ----------------------------
            $header_exists = true;
            xmlwriter_start_element($xw, 'program'); // program start
            xmlwriter_start_attribute($xw, 'language');
            xmlwriter_text($xw, 'IPPcode21');
            xmlwriter_end_attribute($xw);
            continue;
        } else 
            exit(21);
    } else {
        writeInstruction($xw, $income_array, ++$parameters[LOC]); // start xml generation
    }
    $income_array[0] = strtoupper($income_array[0]);

    // parsing instructions
    switch($income_array[0]){
        
        // no parameter
        case 'CREATEFRAME': 
        case 'PUSHFRAME':
        case 'POPFRAME':
        case 'RETURN':
        case 'BREAK':
            NeedLen(ZERO_PARAMETERS);
            break;

        //var
        case 'DEFVAR': 
        case 'POPS': 
            NeedLen(ONE_PARAMETER);
            checkVariable($xw, $income_array, $arg_counter);
            break;

        // symb
        case 'PUSHS':
        case 'WRITE':
        case 'EXIT':
        case 'DPRINT': 
            NeedLen(ONE_PARAMETER);
            checkSymb($xw, $income_array, $arg_counter);
            break;
        
        // var & symb
        case 'MOVE':
        case 'NOT':
        case 'INT2CHAR':
        case 'STRLEN':
        case 'TYPE':
            NeedLen(TWO_PARAMETERS);
            checkVariable($xw, $income_array, $arg_counter++);
            checkSymb($xw, $income_array, $arg_counter);
            break;
            
        // var & type
        case 'READ':
            NeedLen(TWO_PARAMETERS);
            checkVariable($xw, $income_array, $arg_counter++);
            checkType($xw, $income_array, $arg_counter);

            break;

        // var & symb1 & symb2
        case 'ADD':
        case 'SUB':
        case 'MUL':
        case 'IDIV':
        case 'AND':
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'OR':
        case 'STRI2INT':
        case 'CONCAT':
        case 'GETCHAR':
        case 'SETCHAR':
            NeedLen(THREE_PARAMETERS);
            checkVariable($xw, $income_array, $arg_counter++);
            checkSymb($xw, $income_array, $arg_counter++);
            checkSymb($xw, $income_array, $arg_counter);
            break;

        // label & symb1 & symb2
        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':
            $parameters[JUMPS]++;                                   // bonus part
            array_push($jump_array, $income_array[1]);
            if(in_array($income_array[1], $label_array, true)){
                $parameters[BACKJUMPS]++;
            }                                                       // ------

            NeedLen(THREE_PARAMETERS);
            checkLabel($xw, $income_array, $arg_counter++);
            checkSymb($xw, $income_array, $arg_counter++);
            checkSymb($xw, $income_array, $arg_counter);
            break;

        // label
        case 'CALL':
        case 'LABEL':
        case 'JUMP':
            if($income_array[0] == "LABEL"){                          // bonus part
                $parameters[LABELS]++;
                array_push($label_array, $income_array[1]);
                if(in_array($income_array[1], $jump_array, true)){
                    $parameters[FWJUMPS]++;
                }
            } else{
                $parameters[JUMPS]++;
                array_push($jump_array, $income_array[1]);
                if(in_array($income_array[1], $label_array, true)){
                    $parameters[BACKJUMPS]++;
                }                                                     //----
            }
            NeedLen(ONE_PARAMETER);
            checkLabel($xw, $income_array, $arg_counter++);
            break;

        default:
            exit(22);
    }
    xmlwriter_end_element($xw); // instruction end
}
xmlwriter_end_element($xw); // program end
if(!$header_exists)
    exit(21);
echo xmlwriter_output_memory($xw);

$argv_index = 1;                             // bonus part
$fd = null;
$stats_names_array = [];

    // score BADJUMPS
foreach($jump_array as &$jmp){
    if(!in_array($jmp, $label_array, true)){
        $parameters[BADJUMPS]++;
    }
}

// parsing program arguments and writing values for bonus task into file (check if we can access to file)
while($argv_index < $argc){
    if ($argv[1] == "--help")
        break;
    if(preg_match("/^--stats=.*$/", $argv[$argv_index])){
        if($fd)
            fclose($fd);
        $fileName = preg_replace("/^--stats=/", '', $argv[$argv_index]);
        $fileName = trim($fileName, '"');
        if(in_array($fileName, $stats_names_array, true))    // check if is same fileName is already in array of fileNames
            exit(12);
        array_push($stats_names_array, $fileName);  // add fileName to array

        $fd = fopen("$fileName", 'w') or exit(12);

        $argv_index++;
        continue;
    }
    switch($argv[$argv_index]){
        case '--loc':
            fwrite($fd, $parameters[LOC]);
            break;
        case '--comments':
            fwrite($fd, $parameters[COMMENTS]);
            break;
        case '--labels':
            fwrite($fd, $parameters[LABELS]);
            break;
        case '--jumps':
            fwrite($fd, $parameters[JUMPS]);
            break;
        case '--backjumps':
            fwrite($fd, $parameters[BACKJUMPS]);
            break;
        case '--fwjumps':
            fwrite($fd, $parameters[FWJUMPS]);
            break;
        case '--badjumps':
            fwrite($fd, $parameters[BADJUMPS]);
            break;
        default:
            if($fd)
                fclose($fd);
            exit(10);
    }
    $argv_index++;
    fwrite($fd, "\n");
}
if($fd)
    fclose($fd);

exit(0);


        //  -----------------------   A R G U M E N T S   C H E C K   -----------------------
// function check that all arguments are valid and if not, it will exit with error
// $argc - number of arguments
// $argv - arguments value
function arguments_check($argc, $argv){

    if($argc == 2 && $argv[1] == "--help") {
        print("parse.php v jazyce PHP 7.4 načte ze standardního vstupu zdrojový kód v IPPcode21, 
        provede kontrolu lexikální a syntaktické správnosti kódu a vypíše XML reprezentaci programu.\n");
        exit(0);
    } else if ($argc != 1){
        $argv_index = 1;
        if(preg_match("/^--stats=.*$/", $argv[$argv_index])){
            while($argv_index < $argc){
                if(preg_match("/^--stats=.*$/", $argv[$argv_index])){
                    $argv_index++;
                    continue;
                }
                switch($argv[$argv_index++]){
                    case '--loc':
                    case '--comments':
                    case '--labels':
                    case '--jumps':
                    case '--backjumps':
                    case '--fwjumps':
                    case '--badjumps':
                        break;
                    default:
                        exit(10);
                }
            }

        } else
            exit(10);
    }
}

//  -----------------------   F U N C T I O N S   -----------------------

// function will transform incoming string to array and delete from there all white symbols and hashtags (and line till to end after hashtag)
function noSpacesAndHashtag($str){
    $new_str = explode(' ', $str);
    global $parameters;

    $array = [];
    foreach ($new_str as &$element){
        if($element != NULL && $element != ' '){

            if($element[0] == '#'){
                $parameters[COMMENTS]++;
                break;
            }
            if (strpos($element, '#') !== false){
                $parameters[COMMENTS]++;
                $tmp = explode('#', $element);
                array_push($array, trim($tmp[0], "#"));
                break;
            }
                array_push($array, trim($element, "\n"));
        }
    }
    return $array;
}

// load head instructions to xmlwriter buffer
// $xw - xmlwriter buffer
// $income_array - array with instructions and atributes
// $order_counter - variable which counts number of order
function writeInstruction($xw, $income_array, $order_counter){
    xmlwriter_start_element($xw, 'instruction'); // instruction start
    xmlwriter_start_attribute($xw, 'order');
    xmlwriter_text($xw, $order_counter);
    xmlwriter_end_attribute($xw);
    xmlwriter_start_attribute($xw, 'opcode');
    xmlwriter_text($xw, strtoupper($income_array[0]));
    xmlwriter_end_attribute($xw);
}

// check if incoming array has right length
// $needed_length - length which should be for this instruction
function NeedLen($needed_length){
    global $income_array;
    if(count($income_array) != $needed_length)
        exit(23);
}

// check if variables have right format and write xml code to xmlwriter buffer
// $xw - xmlwriter buffer
// $income_array - array with instructions and atributes
// $arg_counter - variable which counts number of arguments
function checkVariable($xw, $income_array, $arg_counter){
    if(preg_match("/^(LF|GF|TF)@[a-zA-Z_\-$&%*!?][0-9a-zA-Z_\-$&%*!?]*$/", $income_array[$arg_counter])){
        xmlwriter_start_element($xw, "arg$arg_counter"); // arg start
        xmlwriter_start_attribute($xw, 'type');
        xmlwriter_text($xw, 'var');
        xmlwriter_end_attribute($xw);
        xmlwriter_text($xw, $income_array[1]);
        xmlwriter_end_element($xw); // arg end
    }  else 
        exit(23);
}

// check if symbols have right format and write xml code to xmlwriter buffer
// $xw - xmlwriter buffer
// $income_array - array with instructions and atributes
// $arg_counter - variable which counts number of arguments
function checkSymb($xw, $income_array, $arg_counter){
    xmlwriter_start_element($xw, "arg$arg_counter"); // arg start
    xmlwriter_start_attribute($xw, 'type');
    
    if(preg_match("/^(LF|GF|TF)@[a-zA-Z_\-$&%*!?][0-9a-zA-Z_\-$&%*!?]*$/", $income_array[$arg_counter])){
        $symb = "var";
        $text = $income_array[$arg_counter];
    } else if(preg_match("/^int@[-+]?[0-9]+$/", $income_array[$arg_counter])){
        $symb = "int";
        $text = preg_replace("/^$symb@/", '', $income_array[$arg_counter]);

    } else if(preg_match("/^string@([^\\\]|[\\\][0-9][0-9][0-9])*$/", $income_array[$arg_counter])){
        $symb = "string";
        $text = preg_replace("/^$symb@/", '', $income_array[$arg_counter]);

    } else if (preg_match("/^bool@(true|false)$/", $income_array[$arg_counter])){
        $symb = "bool";
        $text = preg_replace("/^$symb@/", '', $income_array[$arg_counter]); 
    } else if(preg_match("/^nil@nil$/", $income_array[$arg_counter])){
        $symb = "nil";
        $text = preg_replace("/^$symb@/", '', $income_array[$arg_counter]);
    } else 
        exit(23);

    xmlwriter_text($xw, "$symb");
    xmlwriter_end_attribute($xw);
    xmlwriter_text($xw, $text);
    xmlwriter_end_element($xw); // arg end
}

// check if labels have right format and write xml code to xmlwriter buffer
// $xw - xmlwriter buffer
// $income_array - array with instructions and atributes
// $arg_counter - variable which counts number of arguments
function checkLabel ($xw, $income_array, $arg_counter){
    xmlwriter_start_element($xw, "arg$arg_counter"); // arg start
    xmlwriter_start_attribute($xw, 'type');
    
    if(preg_match("/^[a-zA-Z][a-zA-Z0-9_\-$&%*!?]*$/", $income_array[$arg_counter])){
        $text = $income_array[$arg_counter];
    } else 
        exit(23);

    xmlwriter_text($xw, "label");
    xmlwriter_end_attribute($xw);
    xmlwriter_text($xw, $text);
    xmlwriter_end_element($xw); // arg end
}

function checkType ($xw, $income_array, $arg_counter){
    xmlwriter_start_element($xw, "arg$arg_counter"); // arg start
    xmlwriter_start_attribute($xw, 'type');
    if(preg_match("/^(int|bool|string)$/", $income_array[$arg_counter])){
        $symb = "type";
        $text = preg_replace("/^$symb@/", '', $income_array[$arg_counter]); 
    } else 
        exit(23);

    xmlwriter_text($xw, "$symb");
    xmlwriter_end_attribute($xw);
    xmlwriter_text($xw, $text);
    xmlwriter_end_element($xw); // arg end
}
?>