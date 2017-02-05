from django.db import models
from django.utils import timezone

class Businfo(models.Model):	
	arrival_time = models.DateTimeField()
	weekday = models.CharField(max_length = 2)	
	routeid = models.CharField(max_length = 30)		#identifier of M4101
	stationid = models.CharField(max_length = 30)	
	flag = models.CharField(max_length = 30)

	pno1 = models.CharField(max_length = 30)
	seat1 = models.IntegerField(null=True)
	locno1 = models.CharField(max_length = 5)
	pred1 = models.IntegerField(null=True) #model.IntegerField*(?)

	pno2 = models.CharField(max_length = 30)
	seat2 = models.IntegerField(null=True)
	locno2 = models.CharField(max_length = 5)
	pred2 = models.IntegerField(null=True)

	timestamp = models.IntegerField(default=0)
	waitsec = models.IntegerField(null=True) ###
	pred_diff = models.IntegerField(null=True)
	arrive_flag = models.CharField(max_length = 30)
	
	sta_order = models.IntegerField(null=True)#Order of station

	route = models.CharField(max_length = 10)	#M4101
	dbcreated = models.DateTimeField(auto_now=True) #from str to Integer or CharField
	
	sta_idx = models.IntegerField(null=True)
	delta_boarder = models.IntegerField(null=True)
	boarder = models.IntegerField(null=True)
	full_flag = models.NullBooleanField(null=True)

	def __unicode__(self):
		return self.route + (' : ') + str(self.sta_order)






