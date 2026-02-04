from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

class Model:
    def __init__(self, trainingMail):
        emails = [dict(item, mailbox=mb) for mb, items in trainingMail.items() for item in items]

        self.subjectVectorizer = CountVectorizer()
        subjectX = self.subjectVectorizer.fit_transform([email["subject"] for email in emails])
        self.subjectModel = MultinomialNB()
        self.subjectModel.fit(subjectX, [email["mailbox"] for email in emails])

        self.senderVectorizer = CountVectorizer()
        senderX = self.senderVectorizer.fit_transform([email["sender"] for email in emails])
        self.senderModel = MultinomialNB()
        self.senderModel.fit(senderX, [email["mailbox"] for email in emails])

    def sortBySubject(self, email):
        newSubjectX = self.subjectVectorizer.transform([email["subject"]])
        return self.subjectModel.predict(newSubjectX)[0]

    def sortBySender(self, email):
        newSenderX = self.senderVectorizer.transform([email["sender"]])
        return self.senderModel.predict(newSenderX)[0]

