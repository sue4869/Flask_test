#먼저 static과 templates라는 Directory를 만들어야 한다
#flask : 서버를 구축할 수 있도록 도와주는 프레임워크
#실행하는 순간 내 PC가 서버(html코드 같은 것 서비스한다)의 역활을 한다.

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/test")
def main():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)