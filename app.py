#SQLiteを使用
from flask import Flask
from flask import render_template , request , redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from datetime import datetime
from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import pytz
import os


app = Flask(__name__)

#db定義
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config['SECRET_KEY'] = os.urandom(24) #シークレットキー　暗号化のため
db = SQLAlchemy(app) 
bootstrap = Bootstrap(app)


login_manager = LoginManager()
login_manager.init_app(app) #アプリとの紐づけ


#DBのモデル設定
#ログインのDB
class User(UserMixin , db.Model):
    id = db.Column(db.Integer , primary_key = True)
    username = db.Column(db.String(30) ,unique = True , nullable = False) #30文字まで #uniqueはかぶり無し #nullabllは空でもいいか
    password = db.Column(db.String(12))

#グループ名
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(30) , nullable = False)
    #外部キー
    members = db.relationship('GroupMember', backref='group', lazy=True, foreign_keys='[GroupMember.groupname]')

#グループのメンバー
class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30) , nullable = False)
    groupname = db.Column(db.String(30), db.ForeignKey('group.groupname'))
    
    #制約
    __table_args__ = (
        UniqueConstraint('username', 'groupname', name='uq_username_groupname'),
    )

#支払い
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payer = db.Column(db.String(30))
    recipient = db.Column(db.String(30))
    pay = db.Column(db.String(30))
    cost = db.Column(db.Integer)
    groupname = db.Column(db.String(30), db.ForeignKey('group.groupname'))
    

#そういうもん
@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))


#ログイン画面
@app.route('/' , methods = ['GET','POST'] )
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username = username).first()

        if user:
            # ユーザーが存在する場合
            if check_password_hash(user.password, password):
                # パスワードが正しい場合
                # ログイン成功の処理をここに追加
                login_user(user)
                return redirect('/main')
            else:
                # パスワードが不正解の場合
                # パスワードが不正解のメッセージを返すか、適切なアクションを実行
                return render_template('login.html' , error_message_pass = 'パスワードが間違っています')
        else:
            # ユーザーが存在しない場合
            # ユーザーが不正解のメッセージを返すか、適切なアクションを実行
            return render_template('login.html' , error_message_name = 'ユーザーネームが間違っています')
        
    else:
        return render_template("login.html")
    
    
#サインアップ画面
@app.route('/singup' , methods = ['GET','POST']) #POSTはフォームを送信した時　#GETはWEBページにアクセス
def singup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))

        db.session.add(user) #データベースに追加
        db.session.commit() #変更を保存する　必要
        return redirect('/')
    else:
        return render_template("singup.html")


#メイン画面
@app.route('/main' , methods = ['GET','POST'] )
@login_required
def index():
        return render_template("index.html")
    

#割之介 画面１ グループ作成
@app.route('/warinosuke' , methods = ['GET','POST'] )
@login_required
def warinosuke():
    if request.method == 'POST':
        groupname = request.form.get('groupname')
        usernames = request.form.get('nameList')
        nameList = usernames.split(',')

        group = Group(groupname = groupname)

        for username in nameList:
            user = GroupMember(username = username , groupname = groupname)
            group.members.append(user)

        db.session.add(group)
        db.session.commit()
        return redirect('/warinosuke' + '/' + groupname)        
    
    else:
        return render_template("warinosuke.html")
    

#割之介 画面２　金額画面
@app.route('/warinosuke/<groupname>' , methods = ['GET','POST'] )    
@login_required
def warinosuke1(groupname):
    #usernameだけを取得
    groupmembers = GroupMember.query.filter_by(groupname = groupname).with_entities(GroupMember.username).all()
    #整形
    new_list = [item[0] for item in groupmembers]
   

    #支払い記録
    payers = Payment.query.filter_by(groupname = groupname).with_entities(Payment.payer).all()
    recipients = Payment.query.filter_by(groupname = groupname).with_entities(Payment.recipient).all()
    pays = Payment.query.filter_by(groupname = groupname).with_entities(Payment.pay).all()
    costs = Payment.query.filter_by(groupname = groupname).with_entities(Payment.cost).all()
    # タプル内の要素を取り出してリストに変換
    payers = [item[0] for item in payers]
    recipients = [item[0] for item in recipients]
    pays = [item[0] for item in pays]
    costs = [item[0] for item in costs]

    #かかったお金
    total = {member: 0 for member in new_list}
    #支払ったお金
    paid = {member: 0 for member in new_list}

    #1つ1つデータを見る
    for i in range(len(payers)):
        payer = payers[i]
        recipient = recipients[i].split(',')
        cost = costs[i]
        amount = int(cost) / len(recipient)

        #かかったお金の計算
        for mem in recipient:
            total[mem] += amount


    #かかった金額の大きい順に並び替える
    total_sorted = dict(sorted(total.items(), key=lambda item: item[1], reverse=True))

    # 支払った金額を加算
    for payer, cost in zip(payers, costs):
        paid[payer] += int(cost)

    #結果
    result = {key: total_sorted[key] - paid[key] for key in total_sorted}
    result_sorted = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

    #誰が誰にはらうか
    #負債を持つ人と持たない人を分ける
    creditors = {member: balance for member, balance in result_sorted.items() if balance > 0}
    debtors = {member: -balance for member, balance in result_sorted.items() if balance < 0}

    transactions = []

    # 負債を持つ人から順に、負債を持たない人へお金を渡す
    for debtor, debt in debtors.items():
        #負債があるかぎりループする
        while debt > 0:
            #辞書の一番最初の負債がない人を取得する
            creditor, balance = next(iter(creditors.items()))
            #負債か負債がない人の残高の小さいほうが支払われる
            amount = min(debt, balance)
            transactions.append((creditor, debtor, amount))
            #支払った額を残高から引く
            creditors[creditor] -= amount
            #残高がなくなったら負債のない人の辞書から削除
            if creditors[creditor] == 0:
                del creditors[creditor]
            #負債から支払われた金額を引く
            debt -= amount

    if request.method == 'GET':
        return render_template("warinosuke1.html", groupname = groupname, payers = payers, recipients = recipients, pays = pays, costs = costs , transactions = transactions)


#割之介 入力画面
@app.route('/warinosuke/<groupname>/new' , methods = ['GET','POST'] )    
@login_required
def warinosuke2(groupname):
    #usernameだけを取得
    groupmembers = GroupMember.query.filter_by(groupname = groupname).with_entities(GroupMember.username).all()
    #整形
    new_list = [item[0] for item in groupmembers]

    if request.method == 'GET':
        return render_template("warinosuke2.html", payers = new_list , groupname = groupname)
    
    elif request.method == 'POST':
        payer = request.form.get('payer')
        recipients = request.form.getlist('recipients[]')  # recipients[]の値をリストとして取得
        pay = request.form.get('pay')
        cost = request.form.get('cost')

        # recipientsをカンマ区切りの文字列に変換
        recipients_str = ",".join(recipients)

        payment = Payment(payer = payer, recipient = recipients_str, pay = pay, cost = cost, groupname = groupname)

        db.session.add(payment)
        db.session.commit()
        return redirect('/warinosuke' + '/' + groupname)
    
    
#ログアウト画面
@app.route('/logout')
@login_required #アクセス制限　ログインしている前提
def logout():
    logout_user()
    return redirect('/')


#削除画面
@app.route('/warinosuke/<groupname>/delete', methods = ['GET','POST'])
@login_required
def delete(groupname):
     # 指定したgroupnameを持つGroupの行を削除
    db.session.query(Group).filter(Group.groupname == groupname).delete()
    
    # 指定したgroupnameを持つGroupMemberの行を削除
    db.session.query(GroupMember).filter(GroupMember.groupname == groupname).delete()

    # 変更をコミット
    db.session.commit()

    return redirect('/warinosuke')

#2222
#2222
# flask  --app app run





    

