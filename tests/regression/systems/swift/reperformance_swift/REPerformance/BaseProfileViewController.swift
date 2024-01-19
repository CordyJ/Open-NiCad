//
//  BaseProfileViewController.swift
//
//  Created by Alan Yeung on 2017-05-01.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


class BaseProfileViewController: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    @IBOutlet private var tableView:UITableView?
    
    var lifestyleQuizType:LifestyleQuizType?
    var questionnaireData:QuestionnaireData?
    var internalData:QuestionnaireData = QuestionnaireData(questions: [], questionnaireTitle: "")
    var dismiss: (()->())?
	
	override var preferredStatusBarStyle: UIStatusBarStyle {
		return .lightContent
	}

    var updateProfile: ((LifestyleQuizType, QuestionnaireData)->())?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.tableView?.estimatedRowHeight = 44
		self.tableView?.rowHeight = UITableView.automaticDimension
        
        setUpDoneButton()
    }
    
    func setUpDoneButton(){
        let bottomViewFrame = CGRect(x: 0, y: 0, width: UIScreen.main.bounds.width, height: Constants.Profile.TableViewFooterHeight)
        let bottomView:UIView = UIView(frame: bottomViewFrame)
        let buttonWidth = UIScreen.main.bounds.width * 0.75
        let buttonX = (UIScreen.main.bounds.width/2) - (buttonWidth/2)
        let buttonY = (Constants.Profile.TableViewFooterHeight/2) - (Constants.Profile.TableViewFooterButtonHeight/2)
        let doneButton:UIButton = UIButton(frame: CGRect(x: buttonX, y: buttonY, width: buttonWidth, height: Constants.Profile.TableViewFooterButtonHeight))
        doneButton.setUpOrangeREPerformanceButton()
        doneButton.setTitle("Done", for: .normal)
        doneButton.isUserInteractionEnabled = true
        doneButton.addTarget(self, action: #selector(doneTapped(_:)), for: .touchUpInside)
        bottomView.addSubview(doneButton)
        self.tableView?.tableFooterView = bottomView
    }
    
    @IBAction private func doneTapped(_ sender:UIButton){
        dismiss?()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        if let questionnaireData = self.questionnaireData {
            internalData = questionnaireData
        }
        self.title = internalData.questionnaireTitle
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        
        guard let lifestyleQuizType = lifestyleQuizType else {
            return
        }
        
        switch lifestyleQuizType {
            case .BasicInfo:
                REPAnalytics.trackScreenWithName(screenName: ScreenName.Profile.BasicInfo, className: String(describing: self))
            case .Nutrition:
                REPAnalytics.trackScreenWithName(screenName: ScreenName.Profile.Nutrition, className: String(describing: self))
            case .LifeStyle:
                REPAnalytics.trackScreenWithName(screenName: ScreenName.Profile.Lifestyle, className: String(describing: self))
            case .Exercise:
                REPAnalytics.trackScreenWithName(screenName: ScreenName.Profile.Exercise, className: String(describing: self))
        }
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        guard let lifestyleQuizType = self.lifestyleQuizType else{
            return
        }
        updateProfile?(lifestyleQuizType, internalData)
    }
    
    // MARK: - Table view data source
    
    func numberOfSections(in tableView: UITableView) -> Int {
        return internalData.questions.count
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return internalData.questions[section].possibleAnswers.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "BasicProfileCellIdentifier", for: indexPath)
        
        let answer = internalData.questions[indexPath.section].possibleAnswers[indexPath.row]
        
        cell.textLabel?.text = answer.title
        if(answer.selected) {
            cell.accessoryType = .checkmark
            cell.backgroundColor = UIColor.white
            cell.textLabel?.textColor = UIColor.black
        } else {
            cell.accessoryType = .none
            cell.backgroundColor = UIColor.clear
            cell.textLabel?.textColor = UIColor(named: .rePerformanceWhite)
        }
        return cell
    }
    
    func tableView(_ tableView: UITableView, heightForHeaderInSection section: Int) -> CGFloat {
        
        let titleText:String = internalData.questions[section].questionTitle
        return ProfileHeaderView.getHeightForHeaderView(text: titleText)
    }
    
    func tableView(_ tableView: UITableView, viewForHeaderInSection section: Int) -> UIView? {
        
        let titleText:String = internalData.questions[section].questionTitle
        
        return ProfileHeaderView.getHeaderView(text: titleText)
    }

    //If this function is removed, the viewForHeaderInSection will not call for the first section for some reason.
    func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        return "Section Title"
    }
    
    func tableView(_ tableView: UITableView, willSelectRowAt indexPath: IndexPath) -> IndexPath? {
        
        //allows for deselection of current selection
        var deselectCurrentSelection:Bool = false
        if(internalData.questions[indexPath.section].possibleAnswers[indexPath.row].selected)
        {
            deselectCurrentSelection = true
        }
        
        //Update every value to false to reset for current section
        for index in internalData.questions[indexPath.section].possibleAnswers.indices
        {
            internalData.questions[indexPath.section].possibleAnswers[index].selected = false
        }
        
        //Get all index paths for this section in order to reset every accessoryType to none
        var indexPathsInSection:[IndexPath] = []
        for currentRow in 0..<tableView.numberOfRows(inSection: indexPath.section) {
            indexPathsInSection.append(IndexPath(row: currentRow, section: indexPath.section))
        }
        for currentIndexPath in indexPathsInSection {
            tableView.cellForRow(at: currentIndexPath)?.accessoryType = .none
            tableView.cellForRow(at: currentIndexPath)?.backgroundColor = UIColor.clear
            tableView.cellForRow(at: currentIndexPath)?.textLabel?.textColor = UIColor(named: .rePerformanceWhite)
        }
        
        if(deselectCurrentSelection) {
            //uncheck and leave unchecked
            tableView.cellForRow(at: indexPath)?.accessoryType = .none
            tableView.cellForRow(at: indexPath)?.backgroundColor = UIColor.clear
            tableView.cellForRow(at: indexPath)?.textLabel?.textColor = UIColor(named: .rePerformanceWhite)
        } else {
            //Update answer for section with new value of selected row as true and change accessory type to checkmark
            internalData.questions[indexPath.section].possibleAnswers[indexPath.row].selected = true
            tableView.cellForRow(at: indexPath)?.accessoryType = .checkmark
            tableView.cellForRow(at: indexPath)?.backgroundColor = UIColor.white
            tableView.cellForRow(at: indexPath)?.textLabel?.textColor = UIColor.black
        }
        
        return indexPath
    }

}
