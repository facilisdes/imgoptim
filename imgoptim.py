#!/usr/bin/env python3
import sys
from time import gmtime, strftime
import subprocess
import os

logFile = open("imgoptim.log","a+")
# список игнорируемых подпапок, на случай повторного запуска после сбоя здесь можно указать уже пройденные папки
ignoredSubdirs = ['Largus uni', ""]
# качество выходной картинки, 0-100, где 100 это сжатие без потерь
jpegoptimZipRate = 80
# сила сжатия, 0-7, где 7 - максимальное сжатие
optipngZipRate = 3

def writeToLog(str, forceSave=False):
    logFile.write(strftime("\n%Y-%m-%d %H:%M:%S", gmtime()) + " - " + str)
    # при необходимости сохраняем буфер в файл, иначе пришлось бы ждать окончания работы скрипта.
    # тогда в случае ошибки или зависания начинать пришлось бы заново
    if forceSave:
        logFile.flush()
        os.fsync(logFile.fileno())

def jpegoptim(folder, isRoot = False):
    keyParams = {'shell': True}
    maxDepth = ""
    if isRoot:
        maxDepth = "-maxdepth 1"
    else:
        keyParams['cwd'] = folder

    # find ищет все файлы по маске в текущей папке (она задаётся для подпроцесса, поэтому в вызове find .), для них запускает
    # jpegoptim
    commandString = r'find . %s -type f -iname "*.jpg" -exec jpegoptim --strip-all --all-progressive -pm%d {} \;' % (maxDepth, jpegoptimZipRate)

    subprocess.run(commandString, **keyParams)

def optipng(folder, isRoot = False):
    keyParams = {'shell': True}
    maxDepth = ""
    if isRoot:
        maxDepth = "-maxdepth 1"
    else:
        keyParams['cwd'] = folder

    # аналогично ситуации с jpegoptim
    commandString = r'find . %s -type f -iname "*.png" -exec optipng -strip all -o%d {} \;' % (maxDepth, optipngZipRate)

    subprocess.run(commandString, **keyParams)

try:
    rootDirectory = sys.argv[1]
except IndexError:
    print("No directory passed. Provide a directory to scan - just type it after script name, example: 'imgoptim.py upload'")
    sys.exit()

os.chdir(rootDirectory)
# получаем список содержимого папки, первый индекс - подпапки
subdirsList = next(os.walk('.'))[1]
writeToLog("now working in %s" % rootDirectory)
writeToLog("subfolders scanning, %d folders to optim" % len(subdirsList))
for subdir in subdirsList:
    if subdir in ignoredSubdirs: continue
    writeToLog("*"*10)
    writeToLog("current subfolder is %s" % subdir, True)
    writeToLog("starting jpegoptim on this folder")
    jpegoptim(subdir)
    writeToLog("jpegoptim is done")

    writeToLog("starting optipng on this folder")
    optipng(subdir)
    writeToLog("optipng is done")

writeToLog("*"*10)
writeToLog("now working on root folder (%s)" % rootDirectory, True)
writeToLog("starting jpegoptim")
jpegoptim(rootDirectory, True)
writeToLog("jpegoptim is finished in root")

writeToLog("starting optipng")
optipng(rootDirectory, True)
writeToLog("optipng is finished in root")
writeToLog("%s is optimized\n\n\n" % rootDirectory)
logFile.close()