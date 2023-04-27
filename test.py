def is_ms932(char):
    try:
        print(char , char.encode('MS932').hex(), char.encode('raw_unicode_escape'))
        return True
    except UnicodeEncodeError:
        return False

# print(is_ms932('日'))
# print(is_ms932('咖'))
# print(is_ms932('﨑'))
# print(is_ms932('\ue6f6'))
# print(is_ms932('\ue6f5'))

print(is_ms932('\ue000'))
