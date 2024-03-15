from flask import Flask

app = Flask(__name__)

@app.route("/<name>")
def user(name: str):
    name.strip()
    ans = ""

    lower = True
    upper = True
    onChar = True

    for i in name:
        if i.isalpha():
           ans+=i
        else:
            onChar = False
        if not i.isupper():
            upper = False
        if not i.islower():
            lower = False
    
    if upper:
        ans = ans.lower()
    if lower:
        ans = ans.upper()
    
    if onChar:
        ans = ans[0].upper()+ans.lower()[1:]
    
    return "<h1><strong>Welcome, "+str(ans)+", to my CSCB20 website!</strong></h1>"

if __name__ == "__main__":
    app.run(debug=True)