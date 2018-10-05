def template(file, vars):
    return open(file, 'r').read() % vars