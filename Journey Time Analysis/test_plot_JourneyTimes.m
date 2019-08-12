
weekdaysData = '132_138_60min-weekdays-1.xls';
weekendsData = '132_138_60min-weekends-1.xls';
threshold = 75;
[startEnd, data] = plot_JourneyTimes(weekdaysData, weekendsData, threshold);
