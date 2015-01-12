# read in the top page that contains references to all possible measurements
original.link = "http://www.linz.govt.nz/sea/tides/sea-level-data/sea-level-data-downloads"
root.link = "http://apps.linz.govt.nz/ftp/sea_level_data/"

year = 2014

# reads in the original page
original.page = readLines(original.link)

# finds all hyperlinks starting with http://apps.linz.govt.nz/ftp/sea_level_data/
line.with.links = grep(root.link, original.page,value=TRUE)

# it's only 1 line long... who wrote this webpage?!

# Split it where the link starts, so I can use GSUB
link.splits = strsplit(line.with.links, root.link)
link.splits = unlist(link.splits)

# uses GSUB to remove everything after the potential identifiers
identifiers = gsub("/.*$","",link.splits)

# Get rid of the annoying first link. A little over the top, but more generic
identifiers = identifiers[grepl("^[A-Z]+$",identifiers)]


# Collapse them down to unique identifiers
identifiers = levels(factor(identifiers))




################################################################################
# 	CAN SPLIT HERE
################################################################################
#	but won't :)
################################################################################

library(stringr)

# Creates a list of the webpages where downloads are found (each IDENTIFIER has
# its own webpage which contains the measurements
download.locations = paste(root.link,identifiers,"/",year,"/",identifiers,sep="")

# need to pad zeroes onto 1-99 using library(stringr)
day.numbers = str_pad(1:365, 3, pad = "0")

# need to paste the year onto each day (001-365)
dates = paste(year,day.numbers,sep="")

# paste together the top page of each individual identifier with the zip file
all.downloads = lapply(download.locations, paste, "_",dates,".zip",sep="")

#similar but just adds .csv (since this is what's inside each zip file
all.csvs = lapply(identifiers,paste,"_",dates,".csv",sep="")

################################################################################
# 	CAN SPLIT HERE
################################################################################
#	but won't :)
################################################################################

# Using code from ManDrought
# SHOULD ONLY USE THIS ONCE - 304 MB of data, should probably save as RDS.

read.csv.from.zip = function(file.zip,csv.name,return.as.list=TRUE) {
	temp = tempfile()
	measurements = data.frame(id=numeric(0),datetime=numeric(0),height=numeric(0))

	download.file(file.zip,temp,quiet=TRUE)
	
	tryCatch({	# This is customised!!! Won't work for individual CSVs
			measurements = read.csv(unz(temp,csv.name),
					col.names=c("id","datetime","height"))
			measurements$datetime = as.POSIXct(measurements$datetime)
			},
			error=function(e) {print(paste("ERROR:",file.zip))},
			warning=function(w) {print(paste("WARNING:",file.zip))})

	unlink(temp)

	if(return.as.list) {
		measurements = list(measurements)
	}
	measurements
}

vec.read = Vectorize(read.csv.from.zip)


check.cache = function(name="alltides.rds",save=name) {
	temp = ""
	if (file.exists(name)) {
		temp = readRDS(name)
	} else {
		temp = mapply(vec.read, all.downloads,all.csvs,SIMPLIFY=FALSE)
		saveRDS(temp,save)
	}
	temp
}

all.tides = check.cache()


################################################################################
# 	CAN SPLIT HERE
################################################################################
#	but won't :)
################################################################################

# Talk to Russell Miller

AUCT.set = all.tides[[which(identifiers == "AUCT")]]
CHIT.set = all.tides[[which(identifiers == "TAUT")]]

new.AUCT.set = AUCT.set[[1]]
new.CHIT.set = CHIT.set[[1]]

for(i in 2:7) {
	new.AUCT.set = rbind(new.AUCT.set,AUCT.set[[i]])
	new.CHIT.set = rbind(new.CHIT.set,CHIT.set[[i]])
}

ymin = min(new.AUCT.set$height,new.CHIT.set$height)
ymax = max(new.AUCT.set$height,new.CHIT.set$height)
plot(new.AUCT.set$datetime,new.AUCT.set$height,ylim = c(ymin,ymax),type="l")
lines(new.CHIT.set$datetime,new.CHIT.set$height,col="red")

#tide.ts = ts(new.set$height)
#plot.ts(tide.ts)


#library("TTR")

#new.ts = SMA(tide.ts,n=700)
#plot.ts(new.ts)

#?stl
