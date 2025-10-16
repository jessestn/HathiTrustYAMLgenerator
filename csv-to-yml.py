# This is a modified csv-to-yml.py script that makes several fixes.
# First
#   It makes sure that the times in "Scan Time HH:MM" field in the csv have been properly entered
#   Sometimes Excel will strip the leading zero on 24hr times. Example: 08:45 will be exported as 8:45.
#   This will cause the Hathi ingest to reject the YML file in the SIP. The Hathi SIP Validator does not catch this error. 
#   The script now fixes times that are not properly formated but
#   properly formated times or times with correct 4 digits (11:45) will be left alone. 
# Second
#   Instead of asking for the paths of the csv file and destination path for the generated YML files, 
#   the user adds the csv file location to the command line arguments and the YML files are automatically placed
#   in that same folder. 


import re, os, csv
import sys
from pathlib import Path

# --- Functions from fix_times.py ---
def format_time(time_str):
    """Format time string to ensure leading zero for hours < 10"""
    if not time_str:  # Handle empty strings
        return time_str
    
    # Match times without leading zero (1:15, 9:30, etc.)
    match = re.fullmatch(r'(\d{1,2}):(\d{2})', time_str.strip())
    if match:
        hour, minute = match.groups()
        if len(hour) == 1:  # If hour is single digit
            return f"0{hour}:{minute}"
    return time_str  # Return as-is if already formatted correctly

def process_csv(input_file):
    """Process the CSV file to correct time formats"""
    # Create output file path
    input_path = Path(input_file)
    output_file = input_path.with_name(f"{input_path.stem}_fixed{input_path.suffix}")
    
    try:
        with open(input_file, mode='r', newline='') as infile, \
             open(output_file, mode='w', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            if 'Scan Time HH:MM' not in reader.fieldnames:
                print(f"Error: Column 'Scan Time HH:MM' not found in the CSV file.")
                return False
                
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for row in reader:
                if 'Scan Time HH:MM' in row:
                    row['Scan Time HH:MM'] = format_time(row['Scan Time HH:MM'])
                writer.writerow(row)
                
        print(f"Processed file saved as {output_file}")
        return output_file  # Return the path to the fixed file
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

# --- Original functions from csv-to-yml.py ---
def scanningAndScannerInfo(f):
    global captureDate, scannerMake, scannerModel, scannerUser, bitoneRes, contoneRes, scanningOrder, readingOrder
    if DST.lower() == 'yes' or DST.lower() == 'y':
        DSTOffset = '7'
    else:
        DSTOffset = '8'
    captureDate = 'capture_date: ' + scanYearMonthDay + 'T' + scanTime + ':00-0' + DSTOffset + ':00\n'
    # Default scanner values changed to BookDrive Mark II
    if scannerMakeInput.lower() == 'yes' or scannerMakeInput.lower() == 'y':
        scannerMake = 'scanner_make: Atiz\n'
    else:
        scannerMake = 'scanner_make: ' + scannerMakeInput + '\n'
    if scannerModelInput.lower() == 'yes' or scannerModelInput.lower() == 'y':
        scannerModel = 'scanner_model: BookDrive Mark II\n'
    else:
        scannerModel = 'scanner_model: ' + scannerModelInput + '\n'
    # Default scanner user changed to UWL PS
    scannerUser = 'scanner_user: University of Washington\n'
    if bitoneResInput != '0':
        bitoneRes = 'bitonal_resolution_dpi: ' + bitoneResInput + '\n'
    else:
        bitoneRes = ''
    if contoneResInput != '0':
        contoneRes = 'contone_resolution_dpi: ' + contoneResInput + '\n'
    else:
        contoneRes = ''
    if scanningOrderInput.lower() == 'yes' or scanningOrderInput.lower() == 'y':
        scanningOrder = 'scanning_order: left-to-right\n'
    elif scanningOrderInput.lower() == 'no' or scanningOrderInput.lower() == 'n':
        scanningOrder = 'scanning_order: right-to-left\n'
    else:
        scanningOrder = 'scanning_order: left-to-right\n' #because let's be honest this is the most likely
    if readingOrderInput.lower() == 'yes' or readingOrderInput.lower() == 'y':
        readingOrder = 'reading_order: left-to-right\n'
    elif readingOrderInput.lower() == 'no' or readingOrderInput.lower() == 'n':
        readingOrder = 'reading_order: right-to-left\n'
    else:
        readingOrder = 'reading_order: left-to-right\n' #because let's be honest this is the most likely
    f.write(captureDate)
    f.write(scannerMake)
    f.write(scannerModel)
    f.write(scannerUser)
    if bitoneRes != '':
        f.write(bitoneRes)
    if contoneRes != '':
        f.write(contoneRes)
    f.write(scanningOrder)
    f.write(readingOrder)

def determinePrefixLength(fileNum):
    global prefixZeroes
    if 0 < fileNum < 10:
        prefixZeroes = '0000000'
    elif 10 <= fileNum < 100:
        prefixZeroes = '000000'
    elif 100 <= fileNum < 1000:
        prefixZeroes = '00000'
    elif 1000 <= fileNum < 10000:
        prefixZeroes = '0000'
    else:
        prefixZeroes = 'error'

def generateFileName(prefix, suffix, fileType):
    global fileName
    fileName = prefix + str(suffix) + '.' + fileType.lower()

def generateOrderLabel(fileNum):
    global readingStartNum, readingEndNum, orderNum, orderLabel, romanCap, romanInt, romanStart
    if fileNum == int(readingStartNum):
        orderNum = 1
    if fileNum == int(romanStart):
        romanInt = 1
    orderLabel = ''
    if int(romanCap) != 0:
        if int(romanStart) <= fileNum <= int(romanCap):
            orderLabel = 'orderlabel: "' + toRoman(romanInt) + '"'
            romanInt += 1
        elif int(romanCap) < romanInt:
            orderLabel = ''
    if int(readingStartNum) <= fileNum <= int(readingEndNum) and fileNum not in unpaginatedPages:
        orderLabel = 'orderlabel: "' + str(orderNum) + '"'
        orderNum += 1

def defineMultiWorkLists():
    global readingStartNum, readingEndNum, multiworkStartList, multiworkEndList, romanStartList, romanEndList, romanStart, romanCap
    multiworkStartList = list(map(int, readingStartNum.split(", ")))
    multiworkEndList = list(map(int, readingEndNum.split(", ")))
    readingStartNum = multiworkStartList[0]
    readingEndNum = multiworkEndList[0]
    if ", " in romanStart:
        romanStartList = list(map(int, romanStart.split(", ")))
        romanEndList = list(map(int, romanCap.split(", ")))
        romanStart = romanStartList[0]
        romanCap = romanEndList[0]

def defineMultiworkCycle(fileNum):
    global readingStartNum, readingEndNum, multiworkStartList, multiworkEndList, orderNum, romanStartList, romanEndList, romanStart, romanCap, romanInt
    if fileNum in multiworkEndList:
        if fileNum != multiworkEndList[-1]:
            multiworkStartList.pop(0)
            readingStartNum = multiworkStartList[0]
            multiworkEndList.pop(0)
            readingEndNum = multiworkEndList[0]
    if fileNum in romanEndList:
        if fileNum != romanEndList[-1]:
            romanStartList.pop(0)
            romanStart = romanStartList[0]
            romanEndList.pop(0)
            romanCap = romanEndList[0]

romanNumeralMap = (('m',  1000),
                ('cm', 900),
                ('d',  500),
                ('cd', 400),
                ('c',  100),
                ('xc', 90),
                ('l',  50),
                ('xl', 40),
                ('x',  10),
                ('ix', 9),
                ('v',  5),
                ('iv', 4),
                ('i',  1))

def toRoman(n):
    result = ''
    for numeral, integer in romanNumeralMap:
        while n >= integer:
            result += numeral
            n -= integer
    return result

def fromRoman(s):
    result = 0
    index = 0
    for numeral, integer in romanNumeralMap:
        while s[index:index+len(numeral)] == numeral:
            result += integer
            index += len(numeral)
    return result

def inputToLists():
    global blankPages, chapterPages, chapterStart, copyrightPages, firstChapterStart, foldoutPages, imagePages, indexStart, multiworkBoundaries, prefacePages, referenceStartPages, tableOfContentsStarts, titlePages, halfTitlePages, unpaginatedPages
    if ", " in blankPages:
         blankPages = list(map(int, blankPages.split(", ")))
    else:
        blankPages = [int(blankPages)]
    if ", " in chapterPages:
         chapterPages = list(map(int, chapterPages.split(", ")))
    else:
        chapterPages = [int(chapterPages)]
    if ", " in chapterStart:
         chapterStart = list(map(int, chapterStart.split(", ")))
    else:
        chapterStart = [int(chapterStart)]
    if ", " in copyrightPages:
         copyrightPages = list(map(int, copyrightPages.split(", ")))
    else:
        copyrightPages = [int(copyrightPages)]
    if ", " in firstChapterStart:
         firstChapterStart = list(map(int, firstChapterStart.split(", ")))
    else:
        firstChapterStart = [int(firstChapterStart)]
    if ", " in foldoutPages:
         foldoutPages = list(map(int, foldoutPages.split(", ")))
    else:
        foldoutPages = [int(foldoutPages)]
    if ", " in imagePages:
         imagePages = list(map(int, imagePages.split(", ")))
    else:
        imagePages = [int(imagePages)]
    if ", " in indexStart:
         indexStart = list(map(int, indexStart.split(", ")))
    else:
        indexStart = [int(indexStart)]
    if ", " in multiworkBoundaries:
         multiworkBoundaries = list(map(int, multiworkBoundaries.split(", ")))
    else:
        multiworkBoundaries = [int(multiworkBoundaries)]
    if ", " in prefacePages:
         prefacePages = list(map(int, prefacePages.split(", ")))
    else:
        prefacePages = [int(prefacePages)]
    if ", " in unpaginatedPages:
         unpaginatedPages = list(map(int, unpaginatedPages.split(", ")))
    else:
        unpaginatedPages = [int(unpaginatedPages)]
    if ", " in referenceStartPages:
         referenceStartPages = list(map(int, referenceStartPages.split(", ")))
    else:
        referenceStartPages = [int(referenceStartPages)]
    if ", " in tableOfContentsStarts:
         tableOfContentsStarts = list(map(int, tableOfContentsStarts.split(", ")))
    else:
        tableOfContentsStarts = [int(tableOfContentsStarts)]
    if ", " in titlePages:
         titlePages = list(map(int, titlePages.split(", ")))
    else:
        titlePages = [int(titlePages)]
    if ", " in halfTitlePages:
         halfTitlePages = list(map(int, halfTitlePages.split(", ")))
    else:
        halfTitlePages = [int(halfTitlePages)]

def generateLabel(fileNum):
    global label
    labelList = []
    if fileNum == frontCover:
        labelList.append('"FRONT_COVER"')
    if fileNum == backCover:
        labelList.append('"BACK_COVER"')
    if fileNum in blankPages:
        labelList.append('"BLANK"')
    if fileNum in chapterPages:
        labelList.append('"CHAPTER_PAGE"')
    if fileNum in chapterStart:
        labelList.append('"CHAPTER_START"')
    if fileNum in copyrightPages:
        labelList.append('"COPYRIGHT"')
    if fileNum in firstChapterStart:
        labelList.append('"FIRST_CONTENT_CHAPTER_START"')
    if fileNum in foldoutPages:
        labelList.append('"FOLDOUT"')
    if fileNum in imagePages:
        labelList.append('"IMAGE_ON_PAGE"')
    if fileNum in indexStart:
        labelList.append('"INDEX"')
    if fileNum in multiworkBoundaries:
        labelList.append('"MULTIWORK_BOUNDARY"')
    if fileNum in prefacePages:
        labelList.append('"PREFACE"')
    if fileNum in referenceStartPages:
        labelList.append('"REFERENCES"')
    if fileNum in tableOfContentsStarts:
        labelList.append('"TABLE_OF_CONTENTS"')
    if fileNum in titlePages:
        labelList.append('"TITLE"')
    if fileNum in halfTitlePages:
        labelList.append('"TITLE_PARTS"')
    if not labelList:
        label = ''
    else:
        label = 'label: ' + ', '.join(labelList)

def writeFile():
    global finalNumber, readingStartNum, readingEndNum, fileType, outputFile, romanCap, workingDir, orderNum, multiworkEndList, romanEndList, romanInt
    originalDir = os.getcwd()
    os.chdir(workingDir)
    outputFile = outputFile + '.yml'
    f = open(outputFile, 'w')
    scanningAndScannerInfo(f)
    f.write('pagedata:\n')
    fileNum = 1
    orderNum = 1
    romanInt = 1
    multiworkEndList = [0]
    romanEndList = [0]
    if multiworkBoundaries != 0:
        defineMultiWorkLists()
    inputToLists()
    while fileNum <= finalNumber:
        determinePrefixLength(fileNum)
        generateFileName(prefixZeroes, fileNum, fileType)
        generateOrderLabel(fileNum)
        if multiworkBoundaries != 0:
            defineMultiworkCycle(fileNum)
        generateLabel(fileNum)
        comma = ''
        if orderLabel != '' and label !='':
            comma = ', '
        output = '    ' + fileName + ': { ' + orderLabel + comma + label + ' }\n'
        f.write(output)
        fileNum += 1
    f.close()
    print("File " + outputFile + " created in " + workingDir)
    os.chdir(originalDir)

def gatherInput(csv_path):
    global fileType, workingDir, finalNumber, readingStartNum, readingEndNum, frontCover, outputFile, backCover, blankPages, chapterPages, chapterStart, copyrightPages, firstChapterStart, foldoutPages, imagePages, indexStart, multiworkBoundaries, prefacePages, referenceStartPages, tableOfContentsStarts, titlePages, halfTitlePages, romanStart, romanCap, scanYearMonthDay, scanTime, DST, scannerModelInput, scannerMakeInput, bitoneResInput, contoneResInput, scanningOrderInput, readingOrderInput, unpaginatedPages
    
    # Process the CSV file to fix times
    fixed_csv_path = process_csv(csv_path)
    if not fixed_csv_path:
        print("Error processing CSV file. Exiting.")
        return
    
    # Set working directory to the same folder as the CSV file
    workingDir = str(Path(csv_path).parent)
    
    # Now use the fixed CSV file for processing
    hathi_file = open(fixed_csv_path)
    hathi_csv = csv.reader(hathi_file)
    next(hathi_csv, None)
    
    for row in hathi_csv:
        if row[0] == '':
            outputFile = 'no_barcode'
        else:
            outputFile = row[0]
        if row[1] == '':
            scanYearMonthDay = "0"
        else:
            scanYearMonthDay = row[1]
        if row[2] == '':
            scanTime = "0"
        else:
            scanTime = row[2]
        if row[3] == '':
            DST = "0"
        else:
            DST = row[3]
        if row[6] == '':
            bitoneResInput = "0"
        else:
            bitoneResInput = row[6]
        if row[7] == '':
            contoneResInput = "0"
        else:
            contoneResInput = row[7]
        if row[9] == '':
            scanningOrderInput = 'Y'
        else:
            scanningOrderInput = row[8]
        if row[10] == '':
            readingOrderInput = 'Y'
        else:
            readingOrderInput = row[9]
        if row[11] == '':
            finalNumber = 0
        else:
            finalNumber = int(row[11])
        if row[12] == '':
            frontCover = 0
        else:
            frontCover = int(row[12])
        if row[13] == '':
            halfTitlePages = "0"
        else:
            halfTitlePages = row[13]
        if row[14] == '':
            titlePages = "0"
        else:
            titlePages = row[14]
        if row[15] == '':
            copyrightPages = "0"
        else:
            copyrightPages = row[15]
        if row[16] == '':
            tableOfContentsStarts = "0"
        else:
            tableOfContentsStarts = row[16]
        if row[17] == '':
            romanStart = "0"
        else:
            romanStart = row[17]
        if row[18] == '':
            romanCap = "0"
        else:
            romanCap = row[18]
        if row[19] == '':
            prefacePages = "0"
        else:
            prefacePages = row[19]
        if row[20] == '':
            readingStartNum = "0"
        else:
            readingStartNum = row[20]
        if row[21] == '':
            firstChapterStart = "0"
        else:
            firstChapterStart = row[21]
        if row[22] == '':
            chapterPages = "0"
        else:
            chapterPages = row[22]
        if row[23] == '':
            chapterStart = "0"
        else:
            chapterStart = row[23]
        if row[24] == '':
            readingEndNum = "0"
        else:
            readingEndNum = row[24]
        if row[25] == '':
            blankPages = "0"
        else:
            blankPages = row[25]
        if row[26] == '':
            unpaginatedPages = "0"
        else:
            unpaginatedPages = row[26]
        if row[27] == '':
            imagePages = "0"
        else:
            imagePages = row[27]
        if row[28] == '':
            foldoutPages = "0"
        else:
            foldoutPages = row[28]
        if row[29] == '':
            indexStart = "0"
        else:
            indexStart = row[29]
        if row[30] == '':
            referenceStartPages = "0"
        else:
            referenceStartPages = row[30]
        if row[31] == '':
            multiworkBoundaries = "0"
        else:
            multiworkBoundaries = row[31]
        if row[32] == '':
            backCover = 0
        else:
            backCover = int(row[32])
        if row[10] == '':
            fileType = 'tif'
        else:
            fileType = row[10]
        if row[4] == '':
            scannerMakeInput = 'y'
        else:
            scannerMakeInput = row[4]
        if row[5] == '':
            scannerModelInput = 'y'
        else:
            scannerModelInput = row[5]
        writeFile()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)
    
    # Join all arguments after the script name to handle paths with spaces
    csv_path = ' '.join(sys.argv[1:])
    
    # Check if the path exists (after joining)
    if not os.path.isfile(csv_path):
        print(f"Error: File '{csv_path}' not found.")
        sys.exit(1)
    
    gatherInput(csv_path)
