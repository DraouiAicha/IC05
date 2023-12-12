library(dplyr)

#Table_auteur_topic
author_topic_table <- tt[, c("Handle", "topicMax")]

#Préparatin des données pour créer la table nodes and edges
#table des auteurs
unique_handles <- unique(author_topic_table$Handle)
handle_table <- data.frame(Id = unique_handles, Label = unique_handles, Cat = "auteur")

#table des topics
unique_topics <- unique(author_topic_table$topicMax)
topic_table <- data.frame(Id = unique_topics, Label = unique_topics, Cat = "topic")

#les noms des topics
topic_table <- topic_table %>%
  mutate(Id = case_when(
    Id == "tp1" ~ "Education",
    Id == "tp2" ~ "Innovation",
    Id == "tp3" ~ "Feedback",
    Id == "tp4" ~ "Conseil",
    Id == "tp5" ~ "Publicité",
    TRUE ~ Id  
  ))

topic_table <- topic_table %>%
  mutate(Label = case_when(
    Label == "tp1" ~ "Education",
    Label == "tp2" ~ "Innovation",
    Label == "tp3" ~ "Feedback",
    Label == "tp4" ~ "Conseil",
    Label == "tp5" ~ "Publicité",
    TRUE ~ Label  
  ))

#La table des noeuds
nodes <- rbind(handle_table, topic_table)

#La table des edges
handles <- author_topic_table$Handle
topics <- author_topic_table$topicMax

edges <- cbind(Source = handles, Target = topics, Type = "Undirected")

edges <- edges %>%
  mutate(Target = case_when(
    Target == "tp1" ~ "Education",
    Target == "tp2" ~ "Innovation",
    Target == "tp3" ~ "Feedback",
    Target == "tp4" ~ "Conseil",
    Target == "tp5" ~ "Publicité",
    TRUE ~ Target 
  ))