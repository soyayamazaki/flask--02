function submit() {

    console.log('kkk')

    let payerSelect = document.getElementById('name')
    let payer = payerSelect.options[payerSelect.selectedIndex].value

    let recipientsCheckboxes = document.querySelectorAll('[name="recipients[]"]');
    let recipientChecked = false;

    for (var i = 0; i < recipientsCheckboxes.length; i++) {
        if (recipientsCheckboxes[i].checked) {
            recipientChecked = true;
            break;
        }
    }

    var payInput = document.getElementById('pay').value;
    var costInput = document.getElementById('cost').value;

    if (!payer || !recipientChecked || !payInput || !costInput) {
        return alert('全てのフィールドを入力または選択してください。');
    }


}