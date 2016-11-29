#!/usr/bin/env python
import sys, time, json, requests, getpass, datetime, BeautifulSoup

if len(sys.argv)!=2:
	print 'Please rerun and specifiy in (-i or --in), in-lunch (-iL or--inLunch) or out (-o or --out), out-lunch (-oL or--outLunch)'
	sys.exit()
if (sys.argv[1] != '-i' and sys.argv[1] != '--in') and (sys.argv[1] != '-iL' and sys.argv[1] != '--inLunch') and (sys.argv[1] != '-oL' and sys.argv[1] != '--outLunch') and (sys.argv[1] != '-o' and sys.argv[1] != '--out'):
	print 'Please rerun and enter a valid argument for in (-i or --in), in-lunch (-iL or--inLunch) or out (-o or --out), out-lunch (-oL or--outLunch)'
	sys.exit() 

if sys.argv[1]=='-i' or sys.argv[1]=='--in':
	punchType='ID'
	punchDisplay='In for the Day'
elif sys.argv[1]=='-o' or sys.argv[1]=='--out':
	punchType='OD'
	punchDisplay='Out for the Day'
elif sys.argv[1]=='-iL' or sys.argv[1]=='--inLunch':
	punchType='IL'
	punchDisplay='In from Lunch'
else:
	punchType='OL'
	punchDisplay='Out to Lunch'
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
		'pin':		'',
		'sibling':	'',
		'hobby':	'',
		'car':		'',
		'pet':		''
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

#sheet - need error handling for incorrect entry of secuirty questions
r=session.get('https://www.paycomonline.net/v4/ee/ee-tawebsheet.php?clockid=WEB01&cmdperiodinit=1&session_nonce='+session_nonce,headers=headers)
#get current pay period
soup=BeautifulSoup.BeautifulSoup(r.content)
currentPeriod=str(soup.find("select", { "name" : "periodselect" }).findAll('option')[-1].contents[0])
currentPeriod=currentPeriod.split(' (')[0]
periodStart=currentPeriod.split(' - ')[0]
periodEnd=currentPeriod.split(' - ')[1]

formatPeriodEnd=datetime.datetime.strptime(periodEnd,"%m/%d/%Y")
formatPeriodEnd=formatPeriodEnd + datetime.timedelta(days=1)
periodEndPlusOne=str(formatPeriodEnd.strftime('%m/%d/%Y'))
periodSelect=datetime.datetime.strptime(periodStart,"%m/%d/%Y").strftime('%Y-%m-%d')+'_'+datetime.datetime.strptime(periodEnd,"%m/%d/%Y").strftime('%Y-%m-%d')

currentDay=str(datetime.datetime.now().strftime("%m/%d/%Y"))
todayDateDiffFrmt=datetime.date(int(currentDay.split('/')[-1]),int(currentDay.split('/')[0]),int(currentDay.split('/')[1]))
endDateDiffFrmt=datetime.date(int(periodEndPlusOne.split('/')[-1]),int(periodEndPlusOne.split('/')[0]),int(periodEndPlusOne.split('/')[1]))
startDateDiffFrmt=datetime.date(int(periodStart.split('/')[-1]),int(periodStart.split('/')[0]),int(periodStart.split('/')[1]))
deltaFromEnd = endDateDiffFrmt - todayDateDiffFrmt
deltaFromStart = startDateDiffFrmt - todayDateDiffFrmt

headers={
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, br',
	'Accept-Language':'en-US,en;q=0.8',
	'Cache-Control':'max-age=0',
	'Upgrade-Insecure-Requests':'1',
	'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
}
print "Specify punch time and meridiem"
opNow=raw_input("Valid examples ('now', '02:23 PM' ): ")
if opNow.lower() == 'now':
    punch=str(datetime.datetime.now().strftime("%I:%M %p"))
else:
    punch=opNow
print punch
data={
	'session_nonce':session_nonce,
	'newpunchdatestr':str(datetime.datetime.now().strftime("%m/%d/%Y")),
	'newpunchdateend':'00/00/0000',
	'daysFromTodayStart':deltaFromStart.days, #
	'daysFromTodayEnd':deltaFromEnd.days,   #
	'periodstr':str(periodStart),
	'periodend':str(periodEndPlusOne),
	'newpunchdept':'',
	'jobcategory[1]':'',
	'jobcategory[2]':'',
	'newpunchtype':punchType, #OD (Out) #ID (In)
	'PunchTime':punch,
	'date_time_format':'hh:mm p',
	'newpunchdesc':'',
	'newpunchtaxprof':'0',
	'periodselect':str(periodSelect),
	'approvalday':str(datetime.datetime.strptime(periodStart,"%m/%d/%Y").strftime('%Y-%m-%d')),
	'clockid':'WEB01',
	'cmdaddpunch':'1'
}


print
#print json.dumps(data, indent=4, separators=(',', ': '))
r=session.post('https://www.paycomonline.net/v4/ee/ee-tawebsheet.php',data=data,headers=headers,allow_redirects=False)
if r.status_code == 302:
	print '"Punch" Successful!',punchDisplay,"::",str(datetime.datetime.now().strftime("%I:%M %p")) #display date and time here - and whether in or out
print
