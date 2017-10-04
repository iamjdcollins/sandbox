from datetime import datetime

def currentyear(request):
  currentdate = datetime.now()
  if currentdate.month >= 7:
    currentyearkey = currentdate.year + 1
    currentyearstring = str(currentdate.year) + '-' + str(currentdate.year + 1)[2:]
  else:
    currentyearkey = currentdate.year
    currentyearstring = str(currentdate.year -1) + '-' + str(currentdate.year)[2:]
  currentyear = {"short": currentyearkey, "long": currentyearstring} 
  return {'currentyear': currentyear}
