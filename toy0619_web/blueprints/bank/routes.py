from flask import Blueprint, render_template, request, redirect, session, url_for
from utils.bank_json_manager import load_accounts, save_accounts
from utils import time
import uuid

bank_bp = Blueprint(
    'bank',
    __name__,
    url_prefix='/bank'
)

#newAccount_form_page                      
@bank_bp.route('/newAccount_form', methods=['GET'])
def newAccount_form_page():
    
    mId = session.get('signedId')
    if not mId:
        return redirect(url_for('member.signin_form'))

    newANum = str(uuid.uuid4())
    
    return render_template('bank_forms/newAccount_form.html', aNum = newANum)
         # return render_template('파일경로.html',      HTML용 이름표 = 파이썬데이터)

#newAccount_confirm_process
@bank_bp.route('/newAccount_confirm', methods=['POST'])
def newAccount_confirm_process():

    mId = session.get('signedId')

    if not mId:
        return redirect(url_for('/member.signin_form'))
        
    regdatetime = time.getCurrentDateTime()
    regdate = time.getCurrentDate()

    accdate = time.getCurrentTime()
    
    aNum = request.form['aNum']
    aPw = request.form['aPw']
    
    accounts = load_accounts()

    if mId not in accounts:
        accounts[mId] = {}

    userAccounts = accounts[mId]
     
    userAccounts[aNum] = {
        'aNum' : aNum,
        'aPw' : aPw,
        'bal' : 0,
        'date': accdate,
        'history':{
            regdate : {
                regdatetime : {
                    'dAmount' : 0,
                    'wAmount' : 0
                } 
            }
        }
    }
    

    save_accounts(accounts)

    return render_template('bank_forms/newAccount_result.html', aNum = aNum)

#deposit_form_page
@bank_bp.route('/deposit_form', methods=['GET'])
def deposit_form_page():
    mId = session.get('signedId')
    if not mId:
        return redirect(url_for('member.signin_form'))  # url_for 쓸 때는 /빼기
    
    accounts = load_accounts()
    
    if mId not in accounts or not accounts[mId]:
        
        return redirect(url_for('newAccount_form'))
    
    return render_template('bank_forms/deposit_form.html')

#deposit_confirm_process
@bank_bp.route('/deposit_confirm', methods = ['POST'])
def deposit_confirm_process():

    mId = session.get('signedId')

    if not mId:
        return redirect(url_for('member.signin_form'))

    aNum = request.form['aNum']
    dAmount = int(request.form['dAmount'])

    accounts = load_accounts()

    if mId not in accounts or not accounts[mId]:
        
        return redirect(url_for('newAccount_form'))
        
    userAccounts = accounts.get(mId, {})

    if aNum not in userAccounts:
  
        return render_template('bank_forms/error.html', errorMsg="ACCOUNT NOT FOUND!")

    currentBal = int(userAccounts[aNum]['bal'])

    if dAmount < 0 :
        return render_template('bank_forms/error.html', errorMsg="AMOUNT MUST BE 0 OR MORE!")
    
    regdate = time.getCurrentDate()
    regdatetime = time.getCurrentDateTime()

    if 'history' not in userAccounts[aNum]:
        userAccounts[aNum]['history'] = {}
        
    if regdate not in userAccounts[aNum]['history']:
        userAccounts[aNum]['history'][regdate] = {}

    userAccounts[aNum]['history'][regdate][regdatetime] = {
        'dAmount': dAmount,
        'wAmount': 0
    }

    userAccounts[aNum]['bal'] = currentBal + dAmount

    save_accounts(accounts)

    return render_template('bank_forms/deposit_result.html', dAmount = dAmount)
    
#withdrawal_form_page
@bank_bp.route('/withdrawal_form', methods=['GET'])
def withdrawal_form_page():
    mId = session.get('signedId')
    if not mId:
        return redirect(url_for('member.signin_form'))
    
    accounts = load_accounts()
    
    if mId not in accounts or not accounts[mId]:
        
        return redirect(url_for('newAccount_form'))
    
    return render_template('bank_forms/withdrawal_form.html')

#/bank/withdrawal_confirm_process
@bank_bp.route('/withdrawal_confirm', methods=['POST'])
def withdrawal_confirm_process():

    mId = session.get('signedId')

    if not mId:
        return redirect(url_for('member.signin_form'))

    aNum = request.form['aNum']
    wAmount = int(request.form['wAmount'])

    accounts = load_accounts()

    if mId not in accounts or not accounts[mId]:
        
        return redirect(url_for('newAccount_form'))
        
    userAccounts = accounts[mId]

    currentBal = int(userAccounts[aNum]['bal'])

    if wAmount > currentBal :
        return render_template('bank_forms/error.html', errorMsg="NOT ENOUGH BALANCE!")
    
    regdate = time.getCurrentDate()
    regdatetime = time.getCurrentDateTime()

    if 'history' not in userAccounts[aNum]:
        userAccounts[aNum]['history'] = {}
        
    if regdate not in userAccounts[aNum]['history']:
        userAccounts[aNum]['history'][regdate] = {}

    userAccounts[aNum]['history'][regdate][regdatetime] = {
        'dAmount': 0,
        'wAmount': wAmount
    }

    userAccounts[aNum]['bal'] = currentBal - wAmount

    save_accounts(accounts)

    return render_template('bank_forms/withdrawal_result.html', wAmount = wAmount)  

# /bank/accModify_form_page
@bank_bp.route('/accModify_form')
def accModify_form_page():
    mId = session.get('signedId')
    if not mId:
        return redirect(url_for('member.signin_form'))
    
    accounts = load_accounts()
    
    if mId not in accounts or not accounts[mId]:
   
        return redirect(url_for('newAccount_form'))

    return render_template('bank_forms/accModify_form.html')

#/bank/accModify_confirm
@bank_bp.route('/accModify_confirm', methods=['POST'])
def accModify_confirm_process():

    mId  = session['signedId']
   
    if not mId:
        return redirect(url_for('member.signin_form'))
    
    if mId not in accounts or not accounts[mId]:
   
        return redirect(url_for('newAccount_form'))
    
    aNum = request.form['aNum']
    newAPw = request.form['aPw']
    
    accounts = load_accounts()
    
    userAccounts = accounts.get(mId, {})
    
    if aNum not in userAccounts:
        return render_template('bank_forms/error.html', errorMsg="ACCOUNT NOT FOUND!")
    
    userAccounts[aNum]['aPw'] = newAPw
     
    save_accounts(accounts)
    
    return render_template('bank_forms/accModify_result.html')

@bank_bp.route('/accDelete_form', methods=['GET'])
def delete_form_process_page():

    mId = session.get('signedId')
    if not mId:
        return redirect(url_for('member.signin_form'))
    
    accounts = load_accounts()
    
    if mId not in accounts or not accounts[mId]:
   
        return redirect(url_for('newAccount_form'))

    return render_template('bank_forms/accDelete_form.html')

# /bank/delete_confirm_process
@bank_bp.route('/accDelete_confirm', methods=['POST'])
def delete_confirm_process():

    mId = session.get('signedId')

    if not mId:
        return redirect(url_for('member.signin_form'))
    
    aNum = request.form['aNum']
    
    accounts = load_accounts()

    if aNum in accounts:
        del accounts[aNum]

    save_accounts(accounts)

    return render_template('bank_forms/accDelete_result.html', aNum = aNum)

# /bank/accList_view
@bank_bp.route('/account_list', methods=['GET'])
def accList_view():
    
    mId  = session['signedId']
   
    if not mId:
        return redirect(url_for('member.signin_form'))
    
    accounts = load_accounts()
     
    if mId not in accounts or not accounts[mId]:
        
        return redirect(url_for('newAccount_form'))
    
    userAccounts = accounts.get(mId, {})
    
    account_lists = list(userAccounts.items())
    account_lists.reverse()
    
    return render_template('bank_forms/account_list_result.html', mId = mId, accounts = account_lists)
     
# /bank/account_info/<aNum>
@bank_bp.route('/account_info/<aNum>', methods=['GET'])
def account_infos(aNum):
    mId = session.get('signedId')
    if not mId:
        return redirect(url_for('member.signin_form'))
    
    accounts = load_accounts()

    userAccounts = accounts.get(mId, {})
    
    if aNum not in userAccounts:
        return render_template('bank_forms/error.html', errorMsg="ACCOUNT NOT FOUND!")

    return render_template('bank_forms/account_lnfo.html', account=userAccounts[aNum])
   
       
