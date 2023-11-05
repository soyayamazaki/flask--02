// 名前を保管するための配列
let nameList = [];

function addmember() {
    // フォームから入力値を取得
    let usernameInput = document.getElementById('member');
    let username = usernameInput.value;

    // 名前を配列に追加
    if (nameList.includes(username)){
        alert("同じ名前が既にあります。")
        return usernameInput.value = "";
    } else {
        nameList.push(username);
    }

    if (username) {
        // 入力が空でない場合、リストに名前を追加
        let memberList = document.getElementById('member-list');
        let listItem = document.createElement('div'); // div要素を追加
        let nameItem = document.createElement('p'); // 名前の表示用のp要素
        listItem.classList.add('listItem')
        nameItem.textContent = username;
        listItem.appendChild(nameItem);

        // 削除ボタンを追加
        let deleteButton = document.createElement('button');
        deleteButton.textContent = '削除';
        deleteButton.style.color = 'blue'
        deleteButton.addEventListener('click', function () {
            // 名前を配列から削除
            let index = nameList.indexOf(username);
            if (index !== -1) {
                nameList.splice(index, 1);
            }
            // リストから表示を削除
            listItem.remove();
        });

        listItem.appendChild(deleteButton);

        memberList.appendChild(listItem);

        
        // 入力フィールドをクリア
        usernameInput.value = "";
    } else {
        alert("名前を入力してください。");
    }
}

//JSでPOST送信
function postSend() {
    //グループ名がかぶった時の対処法を入れよう

    let groupnameInput = document.getElementById('groupname')
    let groupname = groupnameInput.value

    //グループ名がなかったら
    if(! groupname) {
        return alert("グループ名を入力してください")
    }

    //メンバーが１人だったら
    if( nameList.length < 2 ) {
        let error_message_member = document.getElementById('error_message_member')
        return error_message_member.innerHTML = '<p style = "font-size: 10px; color: red;">2人以上で作成して下さい</p>'
    }

    let form = document.createElement('form')
    form.method = 'POST'
    form.action = '/warinosuke'

    let request1 = document.createElement('input')
    request1.name = 'groupname'
    request1.value = groupname

    let request2 = document.createElement('input')
    request2.name = 'nameList'
    request2.value = nameList

    form.appendChild(request1)
    form.appendChild(request2)
    document.body.appendChild(form)

    form.submit()

}




