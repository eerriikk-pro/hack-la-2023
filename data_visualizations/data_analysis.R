library(tidyverse)
library(repr)
library(tidymodels)
options(repr.matrix.max.rows = 6)

#this is data for just group members
# update file path appropriately
students <- read.delim("~/Desktop/CPSC/projects/la-hacks-2023/students.csv", sep=",")
View(students)




#preliminary analysis

#count number of rows in the table
row_num <- count(students)
row_num

# check if the data is the same for the feature for all columns
col <- students %>% select(event__extensions_request_id)
filter_col <- col %>% filter(type == "GET")
count(filter_col)

# get rid of these columns to clean up dataframe
# statement_version
# type
# action
# ed_app
# statement_type
# membership_roles
# event__referrer
# event__extensions_request_id

students <- students %>% select(-statement_version, -type, - action, -ed_app,
                                -statement_type, -membership_role, -event__referrer,
                                -event__extensions_request_id, 
                                -event__object_extensions_asset_subtype,
                                -event__object_extensions_http_method)

view(students)



# split event_time into two columns. One for date, and one for time:
# Convert "event_time" to date-time and adjust the time zone to PST

students <- students %>%
  mutate(event_time = as.POSIXct(event_time, format = "%Y-%m-%dT%H:%M:%OSZ", tz = "UTC"),
         event_time_pst = as.POSIXct(format(event_time, tz = "America/Los_Angeles"), tz = "America/Los_Angeles"),
         date = as.Date(event_time_pst),
         time = format(event_time_pst, format = "%H:%M:%OS")) %>%
         select(-event_time)

# the following does not convert to PST from UTC
#students <- students %>%
#  mutate(event_time = as.POSIXct(event_time, format = "%Y-%m-%dT%H:%M:%OSZ"),
#         date = as.Date(event_time),
#         time = format(event_time, format = "%H:%M:%OS")) %>% 
#  select(-event_time)
view(students)


# extract hour from time

students <- students %>%
  mutate(hour = hour(hms(time)))
view(students)

# filter by grades

students_grade_check <- students %>%
  filter(event__object_name == "grades")
view(students_grade_check)
view(students)

# plot histogram for # of grade checks/hour data:

student_grade_check_hist <- ggplot(students_grade_check, aes(x = hour))+
  geom_histogram(binwidth = 1) +
  labs(x = "hour of day", y = "count")+
  theme(text = element_text(size = 20))+
  ggtitle("Grade checking throughout the day")

student_grade_check_hist








# from here, we will use the combined data of the group and the anonymous data

#load anonymous data
anon_students <- read.delim("~/Desktop/CPSC/projects/la-hacks-2023/anonymous_students.csv",
                       sep=",")
View(anon_students)

# process the time related columns as above for anon_students

anon_students <- anon_students %>% select(-statement_version, -type, - action, 
                                          -ed_app, -statement_type,
                                          -membership_role, -event__referrer,
                                          -event__extensions_request_id, 
                                          -event__object_extensions_asset_subtype,
                                          -event__object_extensions_http_method,
                                          -event__attachment_type)
View(anon_students)

anon_students <- anon_students %>%
  mutate(
    event_time = as.POSIXct(anon_students$event_time, tz = "UTC"),
    event_time_pst = with_tz(event_time, tz = "Asia/Bangkok"),
    date = as.Date(event_time_pst),
    time = format(event_time_pst, format = "%H:%M:%S"),
    hour = hour(event_time_pst)
  ) %>%
  select(-event_time)

# count number of students
unique_values <- anon_students %>% distinct(actor_id)
anon_row_num <- count(unique_values)
anon_row_num

View(anon_students)

# alternate code
# anon_students$event_time <- as.POSIXct(anon_students$event_time, tz = "UTC")
# anon_students$event_time_pst <- with_tz(anon_students$event_time, tz = "America/Los_Angeles")
# anon_students$date <- format(anon_students$event_time , format = "%Y-%m-%d", tz = "America/Los_Angeles") 
# anon_students$date <- as.Date(anon_students$date)
# anon_students$time <- format(anon_students$event_time_pst, format = "%H:%M:%S")
# anon_students <- anon_students %>% select(-event_time)
# anon_students <- anon_students %>%
#   mutate(hour = hour(hms(time)))
# View(anon_students)







# plots

# plot histogram for general canvas activity:

student_usage_hist <- ggplot(anon_students, aes(x = hour))+
  geom_histogram(binwidth = 1) +
  labs(x = "hour of day", y = "count")+
  theme(text = element_text(size = 20))+
  ggtitle("Usage throughout the day")

student_usage_hist


# create a new column for the days of the week coressponding to the day

anon_students <- anon_students %>%
  mutate(date = as.Date(date, format = "%Y/%m/%d"),
         day_of_week = weekdays(date))
view(anon_students)

# Create histograms for each day of the week in a grid
weekly_dist <- ggplot(anon_students, aes(x = hour)) +
  geom_histogram(binwidth = 1, fill = "blue", color = "black") +
  facet_wrap(~day_of_week, ncol = 3) +
  labs(
    title = "Hourly Distribution by Day of the Week",
    x = "Hour",
    y = "Count"
  ) +
  theme_minimal()

weekly_dist



# Create histograms for each day of the week in a grid
# additional and optional
person_dist <- ggplot(students, aes(x = hour)) +
  geom_histogram(binwidth = 1, fill = "blue", color = "black") +
  facet_wrap(~name, ncol = 3) +
  labs(
    title = "Hourly Distribution by Day of the Week",
    x = "Hour",
    y = "Count"
  ) +
  theme_minimal()

person_dist


