//
//  LifestyleDataProvider.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-18.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

struct QuestionnaireData{
    let questionnaireTitle:String
    var questions:Array<Question>
    
    init(questions:Array<Question>, questionnaireTitle:String){
        self.questions = questions
        self.questionnaireTitle = questionnaireTitle
    }
}

struct Question {
    let questionTitle: String
    var possibleAnswers: Array<Answer>
    let index: Int
    
    init(possibleAnswers:Array<Answer>, questionTitle:String, index:Int) {
        self.questionTitle = questionTitle
        self.possibleAnswers = possibleAnswers
        self.index = index
    }
}
struct Answer {
    let title: String
    var selected: Bool
    let index: Int
    let points: Int
    
    init(answerTitle: String, answerSelected: Bool, index:Int, points:Int) {
        self.title = answerTitle
        self.selected = answerSelected
        self.index = index
        self.points = points
    }
}

struct BasicInfoData{
    let questionnaireTitle:String
    
    var valueAndUnitsQuestions:Array<ValueAndUnitsQuestion>
    var singleValueQuestions:Array<SingleValueQuestion>
    var normalQuestions:Array<Question>
    
    init(questionnaireTitle:String, valueAndUnitsQuestions:Array<ValueAndUnitsQuestion>, singleValueQuestions:Array<SingleValueQuestion>, normalQuestions:Array<Question>) {
        self.questionnaireTitle = questionnaireTitle
        self.valueAndUnitsQuestions = valueAndUnitsQuestions
        self.singleValueQuestions = singleValueQuestions
        self.normalQuestions = normalQuestions
    }
}

struct ValueAndUnitsQuestion{
    let title:String
    let index:Int
    var valueAnswer:ValueAnswer
    var units:Array<Answer>
    
    init(title:String, index:Int, valueAnswer:ValueAnswer, units:Array<Answer>){
        self.title = title
        self.index = index
        self.valueAnswer = valueAnswer
        self.units = units
    }
    
    func unitSelected() -> Bool {
        var isSelected:Bool = false
        for unit in self.units {
            if unit.selected {
                isSelected = true
                break
            }
        }
        return isSelected
    }
}

struct SingleValueQuestion{
    let title:String
    let index:Int
    var valueAnswer:ValueAnswer
    
    init(title:String, index:Int, valueAnswer:ValueAnswer){
        self.title = title
        self.index = index
        self.valueAnswer = valueAnswer
    }
}

struct ValueAnswer{
    let index:Int
    var value:String?
    
    init(index:Int, value:String?){
        self.index = index
        self.value = value
    }
}

class LifestyleDataProvider: NSObject {
    
    //This must be in the correct order or the constructBasicInfoContent method WILL BREAK
    let basicInfoContent =
        [
            0:["Weight":
                [0:["value":""],
                 1:["title":"lbs", "selected":false, "points":0],
                 2:["title":"Kg", "selected":false, "points":0]]],
            1:["Gender":
                [0:["title":"Male", "selected":false, "points":0],
                 1:["title":"Female", "selected":false, "points":0]]],
            2:["Height":
                [0:["value":""],
                 1:["title":"in", "selected":false, "points":0],
                 2:["title":"cm", "selected":false, "points":0]]],
            3:["Age":
                [0:["value":""]]],
            4:["Country":
                [0:["value":""]]],
            5:["State/Province":
                [0:["value":""]]],
            6:["Where do you work out?":
                [0:["title":"Commercial gym", "selected":false, "points":0],
                 1:["title":"Recreation center", "selected":false, "points":0],
                 2:["title":"Private gym", "selected":false, "points":0],
                 3:["title":"Home", "selected":false, "points":0]]]
    ]
    
    let nutritionContent =
        [
            0:["How many days a week do you pack food?":
                [0:["title":"1", "selected":false, "points":0],
                 1:["title":"2", "selected":false, "points":2],
                 2:["title":"3", "selected":false, "points":4],
                 3:["title":"4+", "selected":false, "points":6]]],
            1:["Rate you nutritional intake?":
                [0:["title":"I eat a balanced diet", "selected":false, "points":6],
                 1:["title":"I think I eat well", "selected":false, "points":4],
                 2:["title":"I don't care what I eat", "selected":false, "points":2],
                 3:["title":"I measure and weigh all my food", "selected":false, "points":8]]],
            2:["How many times a day do you eat protein?":
                [0:["title":"1", "selected":false, "points":0],
                 1:["title":"2", "selected":false, "points":2],
                 2:["title":"3", "selected":false, "points":8],
                 3:["title":"4+", "selected":false, "points":12]]],
            3:["How many times a week do you eat sugary or salty snacks and/or desserts":
                [0:["title":"0", "selected":false, "points":12],
                 1:["title":"1-2", "selected":false, "points":10],
                 2:["title":"3-4", "selected":false, "points":4],
                 3:["title":"5-6", "selected":false, "points":2],
                 4:["title":"5+", "selected":false, "points":0]]],
            4:["Which best describes your appetite:":
                [0:["title":"I eat big meals", "selected":false, "points":6],
                 1:["title":"I eat sparsely", "selected":false, "points":2],
                 2:["title":"I eat small amounts frequently", "selected":false, "points":6],
                 3:["title":"I practise portion control", "selected":false, "points":10]]],
            5:["How many times a week do you eat out?":
                [0:["title":"0-1", "selected":false, "points":10],
                 1:["title":"2-3", "selected":false, "points":8],
                 2:["title":"4-5", "selected":false, "points":4],
                 3:["title":"6-7", "selected":false, "points":2],
                 4:["title":"8+", "selected":false, "points":0]]],
            6:["Rate your water intake:":
                [0:["title":"I don't really like water", "selected":false, "points":2],
                 1:["title":"I never drink water", "selected":false, "points":0],
                 2:["title":"Water is my go to", "selected":false, "points":8]]]
    ]
    
    let lifestyleContent =
        [
            0:["What best describes your sleep?":
                [0:["title":"I sleep okay", "selected":false, "points":4],
                 1:["title":"I'm a restless sleeper", "selected":false, "points":2],
                 2:["title":"I wake up tired", "selected":false, "points":0],
                 3:["title":"I'm a sound sleeper", "selected":false, "points":12]]],
            1:["How many times per week do you feel stressed?":
                [0:["title":"Rarely", "selected":false, "points":12],
                 1:["title":"Sometimes", "selected":false, "points":8],
                 2:["title":"Often", "selected":false, "points":4],
                 3:["title":"Always", "selected":false, "points":2]]],
            2:["How many alcoholic drinks do you have per week?":
                [0:["title":"0-2", "selected":false, "points":12],
                 1:["title":"3-7", "selected":false, "points":6],
                 2:["title":"8-10", "selected":false, "points":4],
                 3:["title":"11+", "selected":false, "points":0]]],
            3:["Do you play recreational sports or have active hobbies?":
                [0:["title":"Yes", "selected":false, "points":8],
                 1:["title":"No", "selected":false, "points":0]]],
            4:["Do you smoke":
                [0:["title":"Yes", "selected":false, "points":0],
                 1:["title":"No", "selected":false, "points":8]]],
            5:["Do you play a sport at the collegiate or professional level?":
                [0:["title":"Yes", "selected":false, "points":12],
                 1:["title":"No", "selected":false, "points":0]]]
    ]
    
    let exerciseContent =
        [
            0:["How long have you been exercising?":
                [0:["title":"0-3 months", "selected":false, "points":0],
                 1:["title":"3 months to 1 year", "selected":false, "points":2],
                 2:["title":"1-3 years", "selected":false, "points":12],
                 3:["title":"3 years plus", "selected":false, "points":18]]],
            2:["How many times per week do you exercise?":
                [0:["title":"1", "selected":false, "points":0],
                 1:["title":"2", "selected":false, "points":2],
                 2:["title":"3", "selected":false, "points":10],
                 3:["title":"4", "selected":false, "points":8],
                 4:["title":"5+", "selected":false, "points":4]]],
            3:["Which best describes your level of intensity?":
                [0:["title":"I don't generally sweat", "selected":false, "points":10],
                 1:["title":"I sweat on and off", "selected":false, "points":2],
                 2:["title":"I sweat the whole time", "selected":false, "points":4]]],
            4:["How long is your workout":
                [0:["title":"0 to 20 minutes", "selected":false, "points":2],
                 1:["title":"20 to 40 minutes", "selected":false, "points":4],
                 2:["title":"40 minutes to 1 hour", "selected":false, "points":6],
                 3:["title":"1 hour +", "selected":false, "points":12]]],
            5:["Does your workout include any of the following?":
                [0:["title":"A personal trainer", "selected":false, "points":3],
                 1:["title":"A work out partner", "selected":false, "points":4],
                 2:["title":"Group class", "selected":false, "points":2],
                 3:["title":"Solo mission", "selected":false, "points":1],
                 4:["title":"Strength and conditioning coach", "selected":false, "points":4]]],
            6:["Describe the way you workout:":
                [0:["title":"Steady state/interval based cardio", "selected":false, "points":2],
                 1:["title":"Cross training/functional fitness", "selected":false, "points":3],
                 2:["title":"Body building", "selected":false, "points":6],
                 3:["title":"Power lifting/olympic lifting", "selected":false, "points":50],
                 4:["title":"Sport specific", "selected":false, "points":8]]]
    ]
    
    //MARK: Interface with persistence layer
    private func constructQuestionnaireData(content:[Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>], questionnaireTitle:String) -> QuestionnaireData? {
        
        var questions:Array<Question> = []
        for (currentQuestionIndex, currentQuestion) in content{
            for (currentQuestionTitle, currentAnswer) in currentQuestion{
                var possibleAnswers:Array<Answer> = []
                for (currentAnswerIndex, currentAnswerBody) in currentAnswer {
                    guard let title:String = currentAnswerBody[Constants.Profile.TitleKey] as? String else {
                        return nil
                    }
                    guard let selected:Bool = currentAnswerBody[Constants.Profile.SelectedKey] as? Bool else {
                        return nil
                    }
                    guard let points:Int = currentAnswerBody[Constants.Profile.PointsKey] as? Int else {
                        return nil
                    }
                    let possibleAnswer:Answer = Answer(answerTitle: title, answerSelected: selected, index: currentAnswerIndex, points: points)
                    possibleAnswers.append(possibleAnswer)
                }
                possibleAnswers.sort(by: sorterForAnswers(a1:a2:))
                let question:Question = Question(possibleAnswers: possibleAnswers, questionTitle:currentQuestionTitle , index: currentQuestionIndex)
                questions.append(question)
            }
        }
        questions.sort(by: sorterForQuestions(q1:q2:))
        return QuestionnaireData(questions: questions, questionnaireTitle: questionnaireTitle)
    }
    
    private func constructPersistenceLayerData(questionnaireData:QuestionnaireData) -> [Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] {
        var content:[Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] = [:]
        for question in questionnaireData.questions{
            var answersToSave: Dictionary<Int, Dictionary<String, Any>> = [:]
            for possibleAnswer in question.possibleAnswers{
                answersToSave[possibleAnswer.index] = [Constants.Profile.TitleKey:possibleAnswer.title, Constants.Profile.SelectedKey:possibleAnswer.selected, Constants.Profile.PointsKey:possibleAnswer.points]
            }
            content[question.index] = [question.questionTitle:answersToSave]
        }
        return content
    }
    
    
    private func constructBasicInfoContent(content:[Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>]) -> BasicInfoData?{
        
        var valueAndUnitsQuestions:Array<ValueAndUnitsQuestion> = []
        var singleValueQuestions:Array<SingleValueQuestion> = []
        var questions:Array<Question> = []
        for (currentQuestionIndex, currentQuestion) in content{
            for (currentQuestionTitle, currentAnswer) in currentQuestion{
                switch currentQuestionIndex {
                case 0, 2:
                    var units:Array<Answer> = []
                    var questionValueAnswer:ValueAnswer?
                    for (currentAnswerIndex, currentAnswerBody) in currentAnswer{
                        switch currentAnswerIndex {
                        case 0:
                            guard let answerValue:String = currentAnswerBody[Constants.Profile.ValueKey] as? String else {
                                return nil
                            }
                            questionValueAnswer = ValueAnswer(index: currentAnswerIndex, value: answerValue)
                        case 1, 2:
                            guard let title:String = currentAnswerBody[Constants.Profile.TitleKey] as? String else {
                                return nil
                            }
                            guard let selected:Bool = currentAnswerBody[Constants.Profile.SelectedKey] as? Bool else {
                                return nil
                            }
                            guard let points:Int = currentAnswerBody[Constants.Profile.PointsKey] as? Int else {
                                return nil
                            }
                            let possibleAnswer:Answer = Answer(answerTitle: title, answerSelected: selected, index: currentAnswerIndex, points: points)
                            units.append(possibleAnswer)
                        default:
                            return nil
                        }
                    }
                    guard let valueAnswer:ValueAnswer = questionValueAnswer else {
                        return nil
                    }
                    units.sort(by: sorterForAnswers(a1:a2:))
                    valueAndUnitsQuestions.append(ValueAndUnitsQuestion(title: currentQuestionTitle, index: currentQuestionIndex, valueAnswer: valueAnswer, units: units))
                case 1, 6:
                    var possibleAnswers:Array<Answer> = []
                    for (currentAnswerIndex, currentAnswerBody) in currentAnswer{
                        guard let title:String = currentAnswerBody[Constants.Profile.TitleKey] as? String else {
                            return nil
                        }
                        guard let selected:Bool = currentAnswerBody[Constants.Profile.SelectedKey] as? Bool else {
                            return nil
                        }
                        guard let points:Int = currentAnswerBody[Constants.Profile.PointsKey] as? Int else {
                            return nil
                        }
                        let possibleAnswer:Answer = Answer(answerTitle: title, answerSelected: selected, index: currentAnswerIndex, points: points)
                        possibleAnswers.append(possibleAnswer)
                    }
                    possibleAnswers.sort(by: sorterForAnswers(a1:a2:))
                    questions.append(Question(possibleAnswers: possibleAnswers, questionTitle: currentQuestionTitle, index: currentQuestionIndex))
                case 3, 4, 5:
                    var questionValueAnswer:ValueAnswer?
                    for (currentAnswerIndex, currentAnswerBody) in currentAnswer{
                        guard let answerValue:String = currentAnswerBody[Constants.Profile.ValueKey] as? String else {
                            return nil
                        }
                        questionValueAnswer = ValueAnswer(index: currentAnswerIndex, value: answerValue)
                    }
                    guard let valueAnswer = questionValueAnswer else {
                        return nil
                    }
                    singleValueQuestions.append(SingleValueQuestion(title: currentQuestionTitle, index: currentQuestionIndex, valueAnswer: valueAnswer))
                default:
                    return nil
                }
            }
        }
        valueAndUnitsQuestions.sort(by: sorterForValueAndUnitsQuestions(q1:q2:))
        singleValueQuestions.sort(by: sorterForSingleValueQuestions(q1:q2:))
        questions.sort(by: sorterForQuestions(q1:q2:))
        return BasicInfoData(questionnaireTitle: "Basic Info", valueAndUnitsQuestions: valueAndUnitsQuestions, singleValueQuestions: singleValueQuestions, normalQuestions: questions)
    }
    
    private func constructPersistenceLayerBasicInfoData(basicInfoData:BasicInfoData) -> [Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] {
        var basicInfoContent:[Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] = [:]
        for valueAndUnitsQuestion in basicInfoData.valueAndUnitsQuestions{
            var valueAnswer:Dictionary<Int, Dictionary<String, Any>> = [:]
            guard let value = valueAndUnitsQuestion.valueAnswer.value else {
                return [:]
            }
            valueAnswer[valueAndUnitsQuestion.valueAnswer.index] = [Constants.Profile.ValueKey:value]
            for possibleAnswer in valueAndUnitsQuestion.units{
                valueAnswer[possibleAnswer.index] = [Constants.Profile.TitleKey:possibleAnswer.title, Constants.Profile.SelectedKey:possibleAnswer.selected, Constants.Profile.PointsKey:possibleAnswer.points]
            }
            basicInfoContent[valueAndUnitsQuestion.index] = [valueAndUnitsQuestion.title:valueAnswer]
        }
        
        for singleValueQuestion in basicInfoData.singleValueQuestions {
            var singleValueAnswer:Dictionary<Int, Dictionary<String, Any>> = [:]
            guard let value = singleValueQuestion.valueAnswer.value else {
                return [:]
            }
            singleValueAnswer[singleValueQuestion.valueAnswer.index] = [Constants.Profile.ValueKey:value]
            basicInfoContent[singleValueQuestion.index] = [singleValueQuestion.title:singleValueAnswer]
        }
        
        for question in basicInfoData.normalQuestions{
            var answersToSave: Dictionary<Int, Dictionary<String, Any>> = [:]
            for possibleAnswer in question.possibleAnswers{
                answersToSave[possibleAnswer.index] = [Constants.Profile.TitleKey:possibleAnswer.title, Constants.Profile.SelectedKey:possibleAnswer.selected, Constants.Profile.PointsKey:possibleAnswer.points]
            }
            basicInfoContent[question.index] = [question.questionTitle:answersToSave]
        }
        return basicInfoContent
    }
    
    func sorterForQuestions(q1:Question, q2:Question) -> Bool {
        return q1.index < q2.index
    }
    
    func sorterForAnswers(a1:Answer, a2:Answer) -> Bool {
        return a1.index < a2.index
    }
    
    func sorterForValueAndUnitsQuestions(q1:ValueAndUnitsQuestion, q2:ValueAndUnitsQuestion) -> Bool {
        return q1.index < q2.index
    }
    
    func sorterForSingleValueQuestions(q1:SingleValueQuestion, q2:SingleValueQuestion) -> Bool {
        return q1.index < q2.index
    }
    
    //MARK: Persistence Layer
    
    func saveBasicInfoData(_ basicInfoData:BasicInfoData){
        
        let paths = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true) as NSArray
        guard let documentDirectory:String = paths[0] as? String else {
            return
        }
        let path = documentDirectory.appending(Constants.Profile.BasicInfoQuestionnaireFilePath)
        
        let basicInfoDict:[Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] = self.constructPersistenceLayerBasicInfoData(basicInfoData: basicInfoData)
        
        NSKeyedArchiver.archiveRootObject(basicInfoDict, toFile:path)
		
		UserDefaults.standard.userAge = getAge(basicInfo: basicInfoData)
        UserDefaults.standard.userWeight = getWeightInPounds(basicInfo: basicInfoData)
        UserDefaults.standard.userGender = getGender(basicInfo: basicInfoData)
        if let countryName = getCountryName(), let provinceName = getProvinceName() {
            UserDefaults.standard.userCurrentLocation = "\(provinceName), \(countryName)"
        } else {
            UserDefaults.standard.userCurrentLocation = ""
        }
    }
    
    func loadBasicInfoData() -> BasicInfoData?{
        let paths = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true) as NSArray
        guard let documentDirectory:String = paths[0] as? String else {
            return self.constructBasicInfoContent(content:self.basicInfoContent)
        }
        let path = documentDirectory.appending(Constants.Profile.BasicInfoQuestionnaireFilePath)
        
        let fileManager = FileManager.default
        if (!(fileManager.fileExists(atPath: path))) {
            return self.constructBasicInfoContent(content:self.basicInfoContent)
        } else {
            guard let unarchivedBasicInfoData:[Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] = NSKeyedUnarchiver.unarchiveObject(withFile: path) as? [Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] else {
                return self.constructBasicInfoContent(content:self.basicInfoContent)
            }
            return self.constructBasicInfoContent(content: unarchivedBasicInfoData)
        }
    }
    
    func saveQuestionnaireData(_ questionnaireData:QuestionnaireData, lifestyleQuizType:LifestyleQuizType){
        let paths = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true) as NSArray
        guard let documentDirectory:String = paths[0] as? String else {
            return
        }
        var filePath:String = ""
        switch lifestyleQuizType{
        case .Nutrition:
            filePath = Constants.Profile.NutritionQuestionnaireFilePath
        case .LifeStyle:
            filePath = Constants.Profile.LifestyleQuestionnaireFilePath
        case .Exercise:
            filePath = Constants.Profile.ExerciseQuestionnaireFilePath
        default:
            return
        }
        let path = documentDirectory.appending(filePath)
        
        let questionnaireDict:[Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] = self.constructPersistenceLayerData(questionnaireData:questionnaireData)
        
        NSKeyedArchiver.archiveRootObject(questionnaireDict, toFile:path)
    }
    
    func loadQuestionnaireData(lifestyleQuizType:LifestyleQuizType) -> QuestionnaireData?{
        var filePath:String = ""
        var content:[Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] = [:]
        var questionnaireTitle:String = ""
        switch lifestyleQuizType{
        case .Nutrition:
            filePath = Constants.Profile.NutritionQuestionnaireFilePath
            content = self.nutritionContent
            questionnaireTitle = Constants.Profile.NutritionQuestionnaireTitle
        case .LifeStyle:
            filePath = Constants.Profile.LifestyleQuestionnaireFilePath
            content = self.lifestyleContent
            questionnaireTitle = Constants.Profile.LifestyleQuestionnaireTitle
        case .Exercise:
            filePath = Constants.Profile.ExerciseQuestionnaireFilePath
            content = self.exerciseContent
            questionnaireTitle = Constants.Profile.ExerciseQuestionnaireTitle
        default:
            return self.constructQuestionnaireData(content: content, questionnaireTitle: questionnaireTitle)
        }
        
        let paths = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true) as NSArray
        guard let documentDirectory:String = paths[0] as? String else {
            return self.constructQuestionnaireData(content: content, questionnaireTitle: questionnaireTitle)
        }
        let path = documentDirectory.appending(filePath)
        
        
        let fileManager = FileManager.default
        if (!(fileManager.fileExists(atPath: path))) {
            return self.constructQuestionnaireData(content: content, questionnaireTitle: questionnaireTitle)
        } else {
            guard let unarchivedQuestionnaireData:[Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] = NSKeyedUnarchiver.unarchiveObject(withFile: path) as? [Int : Dictionary<String, Dictionary<Int, Dictionary<String, Any>>>] else {
                return self.constructQuestionnaireData(content: content, questionnaireTitle: questionnaireTitle)
            }
            return self.constructQuestionnaireData(content: unarchivedQuestionnaireData, questionnaireTitle: questionnaireTitle)
        }
    }
    
    class func wipeAllQuestionnaireDataFromPersistenceLayer(completion: ((_ success:Bool, _ error:String?)->())?) {
        let filePaths:[String] = [Constants.Profile.BasicInfoQuestionnaireFilePath, Constants.Profile.NutritionQuestionnaireFilePath, Constants.Profile.LifestyleQuestionnaireFilePath, Constants.Profile.ExerciseQuestionnaireFilePath]
        let paths = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true) as NSArray
        guard let documentDirectory:String = paths[0] as? String else {
            completion?(false, "Failed to find documents")
            return
        }
        let fileManager = FileManager.default
        for filePath in filePaths{
            let path = documentDirectory.appending(filePath)
            if(fileManager.fileExists(atPath: path)){
                do{
                    try fileManager.removeItem(atPath: path)
                } catch let error as NSError {
                    completion?(false, error.debugDescription)
                    return
                }
            }
        }
        completion?(true, nil)
    }
	
	func getAge(basicInfo: BasicInfoData) -> Int? {
		for question in basicInfo.singleValueQuestions {
			if question.index == Constants.Profile.BasicInfoAgeQuestionIndex {
				guard let age = question.valueAnswer.value else {
					return nil
				}
				
				return Int(age)
			}
		}
		
		return nil
	}
    
    func getWeightInPounds(basicInfo:BasicInfoData) -> Int?{
        for question in basicInfo.valueAndUnitsQuestions{
            if question.index == Constants.Profile.BasicInfoWeightQuestionIndex{
                guard let weight:String = question.valueAnswer.value else {
                    return nil
                }
                for unit in question.units{
                    if unit.index == 2{
                        if unit.selected{
                            guard let weightInKG:Double = Double(weight) else {
                                return nil
                            }
                            let weightInPounds:Double = weightInKG * Constants.Profile.PoundsPerKilogram
                            let rounded:Double = round(weightInPounds)
                            return Int(rounded)
                        }
                    }
                }
                return Int(weight)
            }
        }
        return nil
    }
    
    func getGender(basicInfo:BasicInfoData) -> String? {
        
        for question in basicInfo.normalQuestions{
            if question.index == Constants.Profile.BasicInfoGenderQuestionIndex{
                for answer in question.possibleAnswers{
                    if answer.selected{
                        return answer.title
                    }
                }
            }
        }
        return nil
    }
    
    func checkUnitsComplete(basicInfoQuestionnaire:BasicInfoData) -> (weightComplete:Bool, heightComplete:Bool){

        var weight = true
        var height = true
        for ValueAndUnitsQuestion in basicInfoQuestionnaire.valueAndUnitsQuestions{
            
            if ValueAndUnitsQuestion.index == Constants.Profile.BasicInfoWeightQuestionIndex{
                if ValueAndUnitsQuestion.valueAnswer.value != "" && !ValueAndUnitsQuestion.unitSelected() {
                    weight = false
                }
            }
            if ValueAndUnitsQuestion.index == Constants.Profile.BasicInfoHeightQuestionIndex {
                if ValueAndUnitsQuestion.valueAnswer.value != "" && !ValueAndUnitsQuestion.unitSelected() {
                    height = false
                }
            }
        }
        return (weight, height)
    }
    
    //MARK: Calculate Lifestyle
    
    func sumAllPoints() -> Int?{
        guard let nutritionPoints = totalPointsForLifestyleQuizType(.Nutrition) else {
            return nil
        }
        guard let lifestylePoints = totalPointsForLifestyleQuizType(.LifeStyle) else {
            return nil
        }
        guard let exercisePoints = totalPointsForLifestyleQuizType(.Exercise) else {
            return nil
        }
        let total:Int = nutritionPoints + lifestylePoints + exercisePoints
        if basicInfoQuizComplete(){
            return total
        } else {
            return nil
        }
    }
    
    func totalPointsForLifestyleQuizType(_ lifestyleQuizType:LifestyleQuizType) -> Int?{
        //Any return nil means the questionnaire was not completed, or questionnaire could not be loaded for some reason
        guard let questionnaire:QuestionnaireData = self.loadQuestionnaireData(lifestyleQuizType: lifestyleQuizType) else{
            return nil
        }
        var totalForQuestionnaire:Int = 0
        for question in questionnaire.questions{
            var questionAnswered:Bool = false
            for answer in question.possibleAnswers{
                if answer.selected {
                    totalForQuestionnaire = totalForQuestionnaire + answer.points
                    questionAnswered = true
                }
            }
            if !questionAnswered{
                return nil
            }
        }
        return totalForQuestionnaire
    }
    
    func basicInfoQuizComplete() -> Bool{
        //Any return false means the questionnaire was not completed or questionnaire could not be loaded for some reason
        guard let basicInfoQuestionnaire:BasicInfoData = self.loadBasicInfoData() else {
            return false
        }
        
        for valueAndUnitsQuestion in basicInfoQuestionnaire.valueAndUnitsQuestions{
            if valueAndUnitsQuestion.valueAnswer.value == nil || valueAndUnitsQuestion.valueAnswer.value == "" {
                return false
            }
            var atLeastOneSelected:Bool = false
            for unit in valueAndUnitsQuestion.units{
                if unit.selected {
                    atLeastOneSelected = true
                }
            }
            if !atLeastOneSelected {
                return false
            }
        }
        
        for singleValueQuestion in basicInfoQuestionnaire.singleValueQuestions{
            if singleValueQuestion.valueAnswer.value == nil || singleValueQuestion.valueAnswer.value == "" {
                return false
            }
        }
        
        for question in basicInfoQuestionnaire.normalQuestions {
            var questionAnswered:Bool = false
            for answer in question.possibleAnswers{
                if answer.selected {
                    questionAnswered = true
                }
            }
            if !questionAnswered{
                return false
            }
        }
        
        return true
    }
    
    func getCountryName() -> String?{
        guard let basicInfo:BasicInfoData = self.loadBasicInfoData() else {
            return nil
        }
        for question in basicInfo.singleValueQuestions{
            if question.index == Constants.Profile.BasicInfoCountryQuestionIndex{
                let locations = LocationsDataProvider.loadLoactionsFromFile()
                if let countries = locations?.countries {
                    for country in countries{
                        if country.id == question.valueAnswer.value{
                            return country.name
                        }
                    }
                }
            }
        }
        return nil
    }
    
    func getProvinceName() -> String?{
        guard let basicInfo:BasicInfoData = self.loadBasicInfoData() else {
            return nil
        }
        for question in basicInfo.singleValueQuestions{
            if question.index == Constants.Profile.BasicInfoProvinceQuestionIndex{
                let locations = LocationsDataProvider.loadLoactionsFromFile()
                if let countries = locations?.countries {
                    for country in countries{
                        for province in country.provinces {
                            if province.id == question.valueAnswer.value{
                                return province.name
                            }
                        }
                    }
                }
            }
        }
        return nil
    }
    
    func getCountryID() -> String?{
        guard let basicInfo:BasicInfoData = self.loadBasicInfoData() else {
            return nil
        }
        for question in basicInfo.singleValueQuestions{
            if question.index == Constants.Profile.BasicInfoCountryQuestionIndex{
                return question.valueAnswer.value
            }
        }
        return nil
    }
    
    func getProvinceID() -> String?{
        guard let basicInfo:BasicInfoData = self.loadBasicInfoData() else {
            return nil
        }
        for question in basicInfo.singleValueQuestions{
            if question.index == Constants.Profile.BasicInfoProvinceQuestionIndex{
                return question.valueAnswer.value
            }
        }
        return nil
    }

}
