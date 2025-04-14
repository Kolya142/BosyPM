mkdir $1
echo '{"title": "'$1'", "desc": "My first pkg", "requires": [], "version": "0.0.1", "entry": "install.py"}' > $1/pkg.json
echo "print(\"Installing...\")" > $1/install.py