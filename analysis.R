
# # # # # # # # # # # # # # # # # # # #
# Project: Graduate Admission Analysis
# # # # # # # # # # # # # # # # # # # #

library(SDSRegressionR)

# Import data
adm_data <- read.csv("data/cs_data.csv", stringsAsFactors = FALSE)

# Add new column with binary decision values (0/1)
adm_data$decision_bin <- NA
adm_data$decision_bin[adm_data$decision == "Rejected"] <- 0
adm_data$decision_bin[adm_data$decision == "Accepted"] <- 1

# Factorize Variables
table(adm_data$decision)
adm_data$decision <- factor(adm_data$decision, levels=c("Rejected","Accepted"))

table(adm_data$status)
adm_data$status <- factor(adm_data$status, levels=c("A", "U", "I"))

table(adm_data$degree)
adm_data$degree <- factor(adm_data$degree, levels=c("Masters", "PhD"))

admission <- adm_data[1:500, ]
names(admission)

# Summary
summary(admission)

# Data distribution check
count(admission$degree)
hist(admission$ranking)
hist(admission$year)
hist(admission$gpafin)
hist(admission$gretot)

# Intital Model
adm_mod_0 <- glm(decision ~ gpafin + grev + grem + grew + status + degree + ranking, data=admission, family="binomial")
summary(adm_mod_0)

# Assumption Check
library(car)
vif(adm_mod_0)
cooksPlot(adm_mod_0, key.variable = "id", print.obs = TRUE, sort.obs = TRUE)
threeOuts(adm_mod_0, key.variable = "id")

# Remove outliers
"%not in%" <- Negate("%in%")
g_admission <- admission[admission$id %not in% c('77'),]

# Re-run
adm_mod <- glm(decision ~ gpafin + grev + grem + grew + status + degree + ranking, data=g_admission, family="binomial")
summary(adm_mod)

# Odds-ratios
exp(adm_mod$coef)
exp(confint.default(adm_mod))

# Stats
library(rms)
adm_mod_2 <- lrm(decision ~ gpafin + grev + grem + grew + status + degree + ranking, g_admission)
adm_mod_2

# Pseudo R2
library(DescTools)
PseudoR2(adm_mod, which = "Nagelkerke")

# Test the full categorical variable
library(car)
Anova(adm_mod, type="III")

# Post-hoc testing
library(lsmeans)
lsmeans(adm_mod, "status", type="response")
pairs(lsmeans(adm_mod, "status"), reverse=TRUE, adjust="none")

summary(adm_mod)
ref.grid(adm_mod)

# # PSA
# alpha_PSA <- -5.373861
# beta_PSA  <- 0.032964
# omega_PSA <- (-0.027747 * 66.145) + (-0.014582 * 16.264) + (1.025764 * 6.3669)
# vmark_PSA <- (log(0.50 / (1 - 0.50)) - alpha_PSA - omega_PSA) / beta_PSA
# vmark_PSA
# 
# # GLEASON
# alpha_G <- -5.373861
# beta_G <- 1.025764
# omega_G <- (-0.027747 * 66.145) + (-0.014582 * 16.264) + (0.032964 * 15.377)
# vmark_G <- (log(0.50 / (1 - 0.50)) - alpha_G - omega_G) / beta_G
# vmark_G

# # # # # # # #
# Prediction  #
# # # # # # # #

# Bring in new data:
admission_test <- adm_data[501:510, ]
table(admission_test$decision)
table(admission_test$status)
hist(admission_test$gretot)

odds <- exp(predict(adm_mod, admission_test))
admission_test <- data.frame(admission_test, admission_model=odds/(odds+1))
table(admission_test$id, admission_test$decision, admission_test$admission_model)

# # # # #
# Plots #
# # # # #

# Moderation
# lmDecomp(adm_mod, "statusU", "gpafin", mod.type=2, mod.values = c(1, 2, 3), print.sslopes = FALSE)
# 
# 
# admission_mns_1 <- summary(lsmeans(adm_mod, "gpafin",
#                                  at=list(gpafin = seq(2.45, 4, 0.1)), by="status", type="response"))
# 
# simpleScatter(g_admission, gpafin, decision_bin, ptalpha = 0,
#               title="Quality of Life:Psychological Assessment and State Anxiety by Student Group") +
#   geom_line(data=admission_mns_1, aes(x=gpafin, y=prob, color=status)) +
#   geom_ribbon(data=admission_mns_1, aes(y=prob, ymin=asymp.LCL, ymax=asymp.UCL, group=status), alpha=0.1) 
#   # #Change to your group names and number of groups
#   # scale_colour_manual(name = "Status",
#                       # values =c("red", "blue", "green"),
#                       # labels = c("American, US Degree", "Not American, US Degree", "International"))

# Look at ranges...
summary(g_admission)

# Predict Status
mns <- summary(lsmeans(adm_mod, "status", type="response"))

# Graph Status
library(ggplot2)
ggplot(mns, aes(x=status, y=prob)) +
  geom_bar(stat="identity") +
  geom_errorbar(aes(ymin=asymp.LCL, ymax=asymp.UCL), width=0.2) +
  theme_bw()

# Predict GPA
library(lsmeans)
adm_mns_gpa <- summary(lsmeans(adm_mod, "gpafin",
                                 at=list(gpafin = seq(2, 4, 0.1)), type="response"))

# Graph GPA
g <- simpleScatter(g_admission, gpafin, decision_bin, title="Probability of Admission v. GPA",
                   xlab="GPA", ylab="P(Admission)")
g +
  geom_line(data=adm_mns_gpa, aes(x=gpafin, y=prob), color="red") +
  geom_line(data=adm_mns_gpa, aes(x=gpafin, y=asymp.LCL), linetype="dashed") +
  geom_line(data=adm_mns_gpa, aes(x=gpafin, y=asymp.UCL), linetype="dashed")

# Predict GRE Verbal
adm_mns_grev <- summary(lsmeans(adm_mod, "grev",
                                 at=list(grev = seq(135, 170, 1)), type="response"))

# Graph GRE Verbal
g1 <- simpleScatter(g_admission, grev, decision_bin, title="Probability of Admission v. GRE Verbal Score",
                   xlab="GRE Verbal", ylab="P(Admission)")
g1 +
  geom_line(data=adm_mns_grev, aes(x=grev, y=prob), color="red") +
  geom_line(data=adm_mns_grev, aes(x=grev, y=asymp.LCL), linetype="dashed") +
  geom_line(data=adm_mns_grev, aes(x=grev, y=asymp.UCL), linetype="dashed")

# Predict GRE Math
adm_mns_grem <- summary(lsmeans(adm_mod, "grem",
                                at=list(grem = seq(141, 170, 1)), type="response"))

# Graph GRE Math
g2 <- simpleScatter(g_admission, grem, decision_bin, title="Probability of Admission v. GRE Math Score",
                    xlab="GRE Verbal", ylab="P(Admission)")
g2 +
  geom_line(data=adm_mns_grem, aes(x=grem, y=prob), color="red") +
  geom_line(data=adm_mns_grem, aes(x=grem, y=asymp.LCL), linetype="dashed") +
  geom_line(data=adm_mns_grem, aes(x=grem, y=asymp.UCL), linetype="dashed")

# Predict Ranking
adm_mns_rank <- summary(lsmeans(adm_mod, "ranking",
                                 at=list(ranking=seq(2.2, 5, 0.1)), type="response"))

# Graph Ranking
g3 <- simpleScatter(g_admission, ranking, decision_bin, title="Probability of Admission v. School Ranking",
                   xlab="Ranking", ylab="P(Admission)")
g3 +
  geom_line(data=adm_mns_rank, aes(x=ranking, y=prob), color="red") +
  geom_line(data=adm_mns_rank, aes(x=ranking, y=asymp.LCL), linetype="dashed") +
  geom_line(data=adm_mns_rank, aes(x=ranking, y=asymp.UCL), linetype="dashed")

