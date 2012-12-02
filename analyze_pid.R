#!/usr/bin/env Rscript
#load arguments from command line, if any
args <- commandArgs(trailingOnly=TRUE)
# set options
#options(digits=2)

#
### helper functions
#
# parse input date format
date_parser <- function(x) {return(strptime(x, format="%d/%b/%Y:%H:%M:%S"))}
# convert input to MB
convert <- function(x) {return (x/1024/1024/1024)}

# input arguments
input <- args[1]
time.start <- date_parser(args[2])
time.end <- date_parser(args[3])

data <- read.csv(input, header=T, stringsAsFactors=F)

data$cpu <- as.numeric(sub(pattern="%", replacement="", x=data$cpu))
data$mem <- as.numeric(sub(pattern="%", replacement="", x=data$mem))
data$time <- date_parser(data$timestamp)
data$rss <- sapply(data$rss, convert)
data$vms <- sapply(data$vms, convert)

# slice our data if start/end time boundaries are provided
if  (!is.na(time.start)) {
    data <- subset(data, data$time > time.start)
}
if  (!is.na(time.end)) {
    data <- subset(data, data$time < time.end)
}

cat("CPU summary (percentage):\n")
summary(data$cpu)
cat("RSS summary (GB):\n")
summary(data$rss)
cat("VMS summary (GB):\n")
summary(data$vms)

# make some plots
pdf("summary.pdf")
par(mfrow=c(3,3), oma=c(0,0,2,0)) # c(N,M) N-rows, M-columns
plot(data$time, data$cpu, xlab="Time", ylab="CPU percentage", type="l")
plot(data$time, data$system, xlab="Time", ylab="System time", type="l")
plot(data$time, data$user, xlab="Time", ylab="User time", type="l")
if  (!is.na(time.start)) {
    vec <- c(input, "from", toString(time.start), "to", toString(time.end))
    title(paste(vec, collapse=" "), outer=TRUE)
} else {
    title(input, outer=TRUE)
}
plot(data$time, data$mem, xlab="Time", ylab="MEM percentage", type="l")
plot(data$time, data$rss, xlab="Time", ylab="MEM RSS", type="l")
plot(data$time, data$vms, xlab="Time", ylab="MEM VMS", type="l")
plot(data$time, data$connections.CLOSE_WAIT, xlab="Time", ylab="close_wait", type="l")
plot(data$time, data$connections.ESTABLISHED, xlab="Time", ylab="established", type="l")
plot(data$time, data$connections.LISTEN, xlab="Time", ylab="listen", type="l")
plot(data$time, data$threads, xlab="Time", ylab="# of threads", type="l")
#plot(data$time, data$files, xlab="Time", ylab="# of files", type="l")
plot(data$cpu, data$rss, xlab="CPU", ylab="RSS")
plot(data$cpu, data$vms, xlab="CPU", ylab="VMS")
dev.off()

