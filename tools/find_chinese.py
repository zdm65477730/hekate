import re
import sys
import os


allChineseWords = set({})

for filename in os.listdir("../nyx/nyx_gui/frontend"):
    if filename.endswith('.c'):
        with open('../nyx/nyx_gui/frontend/' + filename, encoding='utf-8') as file:
            content = file.read()
            ll = re.findall('[\u4e00-\u9fa5]', content)
            for w in ll:
                allChineseWords.add(w)

for filename in os.listdir("../bdk/usb"):
    if filename.endswith('.c'):
        with open('../bdk/usb/' + filename, encoding='utf-8') as file:
            content = file.read()
            ll = re.findall('[\u4e00-\u9fa5]', content)
            for w in ll:
                allChineseWords.add(w)

allChineseWords.update(set(list("！（）：”“？；‘，。、")))
for w in allChineseWords:
    print(w, end="")
print("\n")