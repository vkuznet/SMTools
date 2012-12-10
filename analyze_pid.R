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

# Plot the data
# - Specify the layout parameters before any plotting
#   If you don't specify them before any plotting, the
#   results will be inconsistent and misaligned.
#
#
### c(N,M)
#
# - c(N,M) represent plots in N-rows and M-columns
#
### oma
#
# - oma stands for 'Outer Margin Area', or the total margin space that is outside
#   of the standard plotting region (see graph)
#
# - The vector is ordered, the first value corresponding to the bottom. The entire
#   array is c(bottom, left, top, right)
#
# - All of the alternatives are:
#   - oma: Specify width of margins in number of lines
#   - omi: Specify width of margins in inches
#   - omd: Specify width of margins in 'device coordinates'
#       - Device coordinates place (0,0) in the upper left and (1,1) in the
#         lower right corner
#
### mar
#
# - The mar command represents the figure margins. The vector is in the same ordering of
#   the oma commands.
#
# - The default size is c(5,4,4,2) + 0.1, (equivalent to c(5.1,4.1,4.1,2.1)).
#
# - The axes tick marks will go in the first line of the left and bottom with the axis
#   label going in the second line.
#
# - The title will fit in the third line on the top of the graph.
#
# - All of the alternatives are:
#   - mar: Specify the margins of the figure in number of lines
#   - mai: Specify the margins of the figure in number of inches

pdf(paste(input, "pdf", sep="."), onefile=T, paper="USr")
par(mfrow=c(3,3), oma=c(0,0,2,0))
plot(data$time, data$cpu, xlab="Time", ylab="CPU percentage", type="l")
plot(data$time, data$system, xlab="Time", ylab="System time", type="l")
plot(data$time, data$user, xlab="Time", ylab="User time", type="l")
plot(data$time, data$mem, xlab="Time", ylab="MEM percentage", type="l")
plot(data$time, data$rss, xlab="Time", ylab="MEM RSS", type="l")
plot(data$time, data$vms, xlab="Time", ylab="MEM VMS", type="l")
#plot(data$time, data$connections.CLOSE_WAIT, xlab="Time", ylab="close_wait", type="l")
plot(data$time, data$connections.ESTABLISHED, xlab="Time", ylab="established", type="l")
plot(data$time, data$connections.LISTEN, xlab="Time", ylab="listen", type="l")
plot(data$time, data$files, xlab="Time", ylab="# of files", type="l")
#plot(data$time, data$threads, xlab="Time", ylab="# of threads", type="l")
if  (!is.na(time.start)) {
    vec <- c(input, "from", toString(time.start), "to", toString(time.end))
    title(paste(vec, collapse=" "), outer=TRUE)
} else {
    title(input, outer=TRUE)
}
dev.off()

