function [startEnd, data] = plot_JourneyTimes(weekdaysData, weekendsData, threshold )
% Weekdays and weekend data are stored in Excel sheets (no header).
% First column is the temporal unit ID (e.g. 0 indicated 09:00 - 10:00)
% Second column is the journey time of a trip occurred during that interval

% Threshold: Some trips are very long and we clean the datasets by applying
% this threshold to improve lebility of the results.
% Assumption: threshold is fixed regardless the time of day.. it might be
% more possible to have a trip greater than the threshold in rush hour

% Another assumption: we have 24 temporal units - one for each hour

% flag variable is used to differentiate the weekdays and weekends
% flag = 1: weekdays
% flag = 2: weekends


    % Read the data from Excel
    %f_weekdays = '132_138_60min-weekdays-1.xls';
    flag = 1; % weekdays..
    f_weekdays = weekdaysData;
    data{flag} = xlsread(f_weekdays);

    flag = 2; % weekends
    f_weekends = weekendsData;
    data{flag} = xlsread(f_weekends);

    fh = figure;

    tickSize = 20;
    lineWidth = 2;
    counts = zeros(10,1);

    color_outlier = [0.4 0.4 0.4];
    outlierSize = 2;
    % lineWidth = 6; % box plots line width is going to be a variable depending
    % on the number of trips in that time interval!


    for f = 1:2
        numOriginalDataPoints(f) = size(data{f}, 1);
    end


    irregularIDs = {};

    for f = 1:2
        c = 1;
        for i = 1:numOriginalDataPoints(1, f)
            if(data{f}(i,2) > threshold)
                irregularIDs{f}(c) = i;
                c = c + 1;
            end
        end
    end


    for flag = 1:2
        dataClean{flag} = data{flag};
    end
    clear data

    % Remove the trips lasted longer than the threshold
    for flag = 1:2
        dataClean{flag}(irregularIDs{flag}, :) = [];
    end

    for flag = 1:2
        removePerc(flag) = size(dataClean{flag}, 1) / numOriginalDataPoints(flag);
    end


    startEnd = {};
    for flag = 1:2
        st_id = 1;
        startID = 1;
        tID = 1;
        for i = 2:size(dataClean{flag}, 1)
            if((dataClean{flag}(i,1) ~= dataClean{flag}(i-1, 1)))
                startEnd{flag}(tID, 1) = startID;
                startEnd{flag}(tID, 2) = i-1;
                startEnd{flag}(tID, 3) = startEnd{flag}(tID, 2) - startEnd{flag}(tID, 1) + 1;
                startID = i;
                tID = tID + 1;
            end
        end
        % we should also include the last temporal unit's start and end ID
        startEnd{flag}(tID, 1) = startID;
        startEnd{flag}(tID, 2) = size(dataClean{flag}, 1);
        startEnd{flag}(tID, 3) = startEnd{flag}(tID, 2) - startEnd{flag}(tID, 1) + 1;

    end


    % Find the line thicknesses!
    % the thickest has the highest number!

    for flag = 1:2
        [tmp, I] = sort(startEnd{flag}(:,3));
        level = 1;
        for i = 1:24
            startEnd{flag}(I(i), 4) = level;
            level = level + 1;
        end
    end

    % ONE DATA
    % Find the maximum number of trips falling into a temporal unit
    % Regardless whether the day is a weekend or weekday!

    maxTrips = max(max(startEnd{1}(:,3), startEnd{2}(:,3) ));
    data = zeros(maxTrips, 48);
    t_unitID = 1;
    for i = 1:2:48
        for flag = 1:2
            interval = [startEnd{flag}(t_unitID, 1) startEnd{flag}(t_unitID, 2)];
            numTrips = startEnd{flag}(t_unitID, 3);
            data(1:numTrips, i + flag - 1) = dataClean{flag}(interval(1):interval(2), 2);
            data(numTrips+1:end, i + flag - 1) = NaN;
        end
        % Move on to the next temporal unit ID
        t_unitID = t_unitID + 1;
    end


    % Positions

    startPos = 1;
    increment = 0.1;

    m=1;
    lp = 1; % index of the label position
    for i=1:24
        positions(m) = startPos;
        positions(m+1) = startPos + increment;
        labelPositions(lp) = startPos + increment/2; 
        startPos = startPos + increment*3; 
        m= m+2;
        lp = lp + 1;
    end

    % Colours - weekdays - weekends
    % colors = [50/288 102/288 144/288;
    %           96/288 177/288 80/288];

    colors = [255/288 37/288 0/288;
              50/288 102/288 144/288];


    % Line thickness - based on the number of trips used to generate the box
    % Consider as a stack - the last temporal unit ID (i.e. weekends - 23-24)
    % has an ID of 1
    lineThickness = [];
    boxID = 1;
    thicknessScaler = 3.5;
    for i = 24:-1:1
        lineThickness(boxID) = startEnd{2}(i, 4) / thicknessScaler;
        lineThickness(boxID+1) = startEnd{1}(i, 4) / thicknessScaler;
        boxID = boxID + 2;

    end


    labels = {'00:00-01:00', '', '', '03:00-04:00', '', '', '06:00-07:00', '', '', '09:00-10:00', '', '', '12:00-13:00', '', '', '15:00-16:00', '', '', '18:00-19:00',  '', '', '21:00-22:00', '', ''};


    bp = boxplot(data, 'positions', positions, 'Color', colors,'outliersize', outlierSize);

    % Additional parameters:
    % 'BoxStyle','filled' - no box, but a line.. its thickness is fixed IMO

    % Arrange the thickness of the boxes
    boxes = findobj(gcf, 'tag', 'Box');
    u_whisker = findobj(gcf, 'tag', 'Upper Whisker');
    l_whisker = findobj(gcf, 'tag', 'Lower Whisker');
    med = findobj(gcf, 'tag', 'Median');

    whiskerAdjuster = 0.4;
    for i = 1:48
        boxes(i,1).LineWidth = lineThickness(i);
        u_whisker(i,1).LineWidth = lineThickness(i) * whiskerAdjuster;
        l_whisker(i,1).LineWidth = lineThickness(i) * whiskerAdjuster;
        med(i,1).LineWidth = lineThickness(i);
    end

    % Outlier coloring
    h = findobj(gcf,'tag','Outliers');
    for iH = 1:length(h)
        h(iH).MarkerEdgeColor = color_outlier;
        h(iH).Marker = 'o';
    end



     % Set the labels
    set(gca, 'XTick', labelPositions)
    set(gca, 'XTickLabel', labels);

    % Tick label rotation: https://www.mathworks.com/matlabcentral/answers/231538-how-to-rotate-x-tick-label
    %set(gca,'XTickLabelRotation',10)

    set(fh, 'color', 'white'); % sets the color to white 
    set(gca, 'Box', 'off'); % here gca means get current axis 
    set(gca, 'FontSize', tickSize);
    set(gca,'LineWidth',lineWidth);


    labelSize = 26;
    ylabel('Journey Time (minutes)', 'FontSize', labelSize);
    xlabel('Time Intervals', 'FontSize', labelSize);



    set(gca, 'YGrid','on', 'GridLineStyle', '--');

    set(gcf,'units','normalized','outerposition',[0 0 1 1]); %frames the figure into the computer screen - not a complete maximize, but works fine -when opening the figure, it opens as big scale (but not maximized)

    hold on
    h = zeros(2, 1);
    h(1) = plot(2,2,'-', 'Color', colors(1,:), 'visible', 'off');
    h(2) = plot(2,2,'-', 'Color', colors(2,:),  'visible', 'off');
    % Adjustment of line thickness in the legend
    % https://www.mathworks.com/matlabcentral/answers/328791-how-do-i-change-the-linewidth-and-the-fontsize-in-a-legend
    %legendSize = 20; %legend is quite small
    [hleg, hobj, hout, mout] = legend('Weekdays','Weekends');
    
    % To update the font in the legend:
    % https://www.mathworks.com/matlabcentral/answers/313678-how-do-i-change-the-font-in-my-legend-possible-bug
    temp = [hleg; hleg.ItemText];
    set(temp, 'FontSize', 24)
    %set(temp, 'FontName', 'Times New Roman')
    
    set(hobj,'linewidth',6);
    
    set(hleg,'position',[0 0 0.16 0.10])


    % Adjust the y-limits to improve visualisation
    ylim([8 73])
    
    % Reduce the white space while saving the figure
    % https://www.mathworks.com/help/matlab/creating_plots/save-figure-with-minimal-white-space.html
    reduceWhiteSpace();
    

end % EOF function

