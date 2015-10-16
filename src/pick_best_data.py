def pick_best(name, api, data):
    if api.name == "hummingbirdv1":
        done = False
        maxb = 3
        best = data[0]
        if not(best['title'].lower() == name.lower() or best['title'] == name.lower()):
            for e in data:
                if not e['alternate_title']:
                    e['alternate_title'] = ""
                for j in reversed(range(maxb,len(name))):
                    for k in range(0,len(name),j):
                        if k+j<len(name) and (name[k:k+j+1].lower() in e['title'].lower() or name[k:k+j+1].lower() in e['alternate_title'].lower()):
                            if j > maxb:
                                maxb, best = j, e
                            break
        return best
