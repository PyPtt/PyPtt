import PTTUtil

Content = PTTUtil.readPostFile('uao250-u2b.txt')

Big5ToUnicode = ''
UnicodeToBig5 = ''

for target_list in Content.split('\r\n'):
    if target_list.startswith('#'):
        continue
    Big5ToUnicode += '\t' + target_list.replace(' ', ': ') + ',\n'

    UnicodeList = target_list.split(' ')
    UnicodeToBig5 += '\t' + UnicodeList[1] + ': ' + UnicodeList[0] + ',\n'

with open("Big5ToUnicode.txt", "w") as file:
    file.write(Big5ToUnicode)

with open("UnicodeToBig5.txt", "w") as file:
    file.write(UnicodeToBig5)

# print(Content)