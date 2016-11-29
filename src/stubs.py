#!/usr/bin/env python
import sys, time, getpass, requests, BeautifulSoup

session=requests.session()
email=raw_input('Username/Email: ')
passwd=getpass.getpass()
ssn=getpass.getpass('Last 4 of SSN: ')

data={
	'username':email,
	'userpass':passwd,
	'userpin':ssn,
	'submit':'Log in'
}

headers={
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, br',
	'Accept-Language':'en-US,en;q=0.8',
	'Cache-Control':'max-age=0',
	'Referer':'https://www.paycomonline.net/v4/ee/ee-login.php',
	'Upgrade-Insecure-Requests':'1',
	'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
}

r=session.post('https://www.paycomonline.net/v4/ee/ee-loginproc.php',data=data,headers=headers)
time.sleep(2)
r=session.get('https://www.paycomonline.net/v4/ee/ee-secquest-login.php?session_nonce=',headers=headers)
try:
	#logic here to auto answer
	#populate fields here to avoid answering questions every punch
	my_answers={
		'pin':		'##################',
		'sibling':	'##################',
		'hobby':	'##################',
		'car':		'##################',
		'pet':		'##################'
	}
	session_nonce=r.content.split("SessionNonceJS.initialize('")[1].split("');")[0]
	q1=r.content.split('<div class="col-md-6 nopad">\r\n')[1].split('</div>')[0]
	for key in my_answers.keys():
		if key in q1:
			ans1=my_answers[key]
	ans1=raw_input(q1)
	q2=r.content.split('<div class="col-md-6 nopad">\r\n')[3].split('</div>')[0]
	for key in my_answers.keys():
		if key in q2:
			ans2=my_answers[key]
	ans2=raw_input(q2)
except:
	print "Incorrect answers"

data={
	'sansw1':ans1,
	'sansw2':ans2,
	'cmdupdate':'Loading...',
	'session_nonce':session_nonce
}

r=session.post('https://www.paycomonline.net/v4/ee/ee-secquest-loginproc.php',data=data,headers=headers)
r=session.get('https://www.paycomonline.net/v4/ee/ee-menu.php',headers=headers)

r=session.get('https://www.paycomonline.net/v4/ee/ee-checklist.php?session_nonce='+session_nonce,headers=headers)
r=session.get('https://www.paycomonline.net/v4/ee/ee-mccchecklistajax.php?session_nonce='+session_nonce+'&reportyear=2016&startdate=2016-01-01&enddate=2016-12-31')

soup=BeautifulSoup.BeautifulSoup(r.content)
check_table=soup.findAll("button", { "id" : "viewEarnings" })
count=1
for stub in check_table:
	r=session.get('https://www.paycomonline.net/v4/ee/'+stub['onclick'].split("window.open('")[1].split("');")[0]+'&topdf=2',headers=headers)
	with open("statement"+str(count)+".pdf", "wb") as code:
		code.write(r.content)
	print "Downloaded statement"+str(count)+".pdf"
	count+=1
