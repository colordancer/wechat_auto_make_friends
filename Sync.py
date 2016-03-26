def updateKey(old, new):
    dic = {}
    for key in old['List']:
        dic[key['Key']] = key['Val']
    for key in new['List']:
        dic[key['Key']] = key['Val']
    result = []
    for key in dic:
        result.append({'Key': key, 'Val': dic[key]})
    result = sorted(result, key=(lambda x: x['Key']))
    old['List'] = result
    old['Count'] = len(result)
    print(old)
    print('\n\n')

def getStringKey(keys):
    result = []
    for key in keys['List']:
        if result:
            result.append('|')
        result.append(str(key['Key']))
        result.append('_')
        result.append(str(key['Val']))
    return ''.join(result)