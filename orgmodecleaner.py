import os
import re

directory = ''  # local directory
extensions = ['.org']
makebackup = True
simulate = False


def get_files():
    files = []
    allfilenames = os.listdir(directory + '.')
    for fi in allfilenames:
        ext = os.path.splitext(fi)[1]
        # check if file of proper extension
        if ext.lower() in extensions:
            files.append(fi)
    # returns a lists of file objects
    return files


def removemultiplelines(fn):
    changed = False
    with open(fn) as orig:
        out = orig.read()
        patternlist = [
            (r' +\n', r'\n'),
            (r'\n{3,}', r'\n\n'),
            (r'\n{2,}$', r'\n')
        ]
        for pat in patternlist:
            if re.search(pat[0], out):
                out = re.sub(pat[0], pat[1], out)
                changed = True
        if not changed:
            return False
        if not simulate:
            tmpfn = f"{fn}.tmp"
            with open(tmpfn, mode="w") as tmpf:
                tmpf.write(out)
            if makebackup:
                os.rename(fn, f"{fn}.bak")
            else:
                os.remove(fn)
            os.rename(tmpfn, fn)
        print(f"  Removed multiple lines in: {fn}...")
        return True


def hastitletag(fn):
    with open(fn) as file:
        data = file.read()
        basetitle = r' *\#\+title: *'
        if not re.search(basetitle, data):
            return False
        else:
            return True


def hastitle(fn):
    with open(fn) as file:
        data = file.read()
        basetitle = r' *\#\+title: *'
        pattern = basetitle + r'[^\s]'
        if not re.search(pattern, data):
            return False
        else:
            return True


def capableofgettingtitle(fn):
    with open(fn) as file:
        data = file.read()
        basetitle = r' *\#\+title: *'
        pattern = basetitle + r'\s*\#{1}'
        if re.search(pattern, data):
            return True
        else:
            return False


def getnewtitle(fn):
    with open(fn) as orig:
        data = orig.read()
        pattern = r'( *\#\+title:) *\s*\#{1}'
        out = re.sub(pattern, r'\1', data)
        tmpfn = f"{fn}.tmp"
        with open(tmpfn, mode="w") as tmpf:
            tmpf.write(out)
        if makebackup:
            os.rename(fn, f"{fn}.bak")
        else:
            os.remove(fn)
        os.rename(tmpfn, fn)
        return True


def metatitle(fn):
    if hastitletag(fn):
        if not hastitle(fn):
            if capableofgettingtitle(fn):
                if getnewtitle(fn):
                    print(f"  {fn} has a new title")
                    return True


def containshashheadings(fn):
    with open(fn) as orig:
        data = orig.read()
        pattern = r'\n *\#{1,6} *\w'
        if re.search(pattern, data):
            print(f"  {fn} contains hash headings")
            return True
        else:
            return False


def fixheadings(fn):
    with open(fn) as orig:
        lines = orig.readlines()
        tmpfn = f'{fn}.tmp'
        pattern = r'^( *)(#{1,})([^+].*)$'
        outlist = []
        for line in lines:
            if re.search(pattern, line):
                m = re.match(pattern, line)
                hashstr = m.group(2)
                lenhashstr = len(hashstr)
                if lenhashstr > 1:
                    lenhashstr -= 1
                starstr = lenhashstr * '*'
                newline = m.group(1) + starstr + m.group(3) + '\n'
                outlist.append(newline)
            else:
                outlist.append(line)
    if not simulate:
        with open(tmpfn, mode='w+') as dest:
            for line in outlist:
                dest.write(line)
        if makebackup:
            os.rename(fn, f"{fn}.bak")
        else:
            os.remove(fn)
        os.rename(tmpfn, fn)
    print(f"  > replaced heading markers in {fn}")
    return True


def main():
    files = get_files()
    count = 0
    for fn in files:
        if metatitle(fn):
            count += 1
        if removemultiplelines(fn):
            count += 1
        if containshashheadings(fn):
            if fixheadings(fn):
                count += 1

    print(f"\nChanged {count} file(s)")


if __name__ == "__main__":
    main()
