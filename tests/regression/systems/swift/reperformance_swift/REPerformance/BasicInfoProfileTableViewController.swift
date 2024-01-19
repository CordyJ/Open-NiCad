//
//  BasicInfoProfileTableViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-11.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class BasicInfoProfileTableViewController: UIViewController, UITableViewDataSource, UITableViewDelegate {
    
    @IBOutlet var tableView:UITableView?
    
    var basicInfoData:BasicInfoData?
    var internalData:BasicInfoData =  BasicInfoData(questionnaireTitle: "", valueAndUnitsQuestions: [], singleValueQuestions: [], normalQuestions: [])
    
    var locations:Locations?
    
    var updateProfile: ((BasicInfoData)->())?
    var locationCell:((LocationDisplay)->())?
    var dismiss: (()->())?


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
        if let basicInfoData = self.basicInfoData {
            internalData = basicInfoData
        }
        self.title = internalData.questionnaireTitle
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        updateProfile?(internalData)
    }

    func numberOfSections(in tableView: UITableView) -> Int {
        return internalData.valueAndUnitsQuestions.count + internalData.singleValueQuestions.count + internalData.normalQuestions.count
    }

    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        
        switch section{
        case 0, 2, 3, 4, 5:
            return 1
        case 1, 6:
            for question in internalData.normalQuestions{
                if question.index == section{
                    return question.possibleAnswers.count
                }
            }
        default:
            return 0
        }
        return 0
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        
        let defaultCell:UITableViewCell = UITableViewCell.init(style: .default, reuseIdentifier: "default")
        defaultCell.textLabel?.text = "Error"

        switch indexPath.section{
        case 0:
            guard let valueAndUnitsCell:ValueAndUnitsTableViewCell = tableView.dequeueReusableCell(withIdentifier: Constants.Profile.ValueAndUnitsProfileCellIdentifier, for: indexPath) as? ValueAndUnitsTableViewCell else {
                return defaultCell
            }
            
            valueAndUnitsCell.valueFieldChanged = {newValue in
                for index in self.internalData.valueAndUnitsQuestions.indices{
                    if self.internalData.valueAndUnitsQuestions[index].index == indexPath.section{
                        self.internalData.valueAndUnitsQuestions[index].valueAnswer.value = newValue
                    }
                }
            }
            
            valueAndUnitsCell.checkboxChanged = {
                for index in self.internalData.valueAndUnitsQuestions.indices{
                    if self.internalData.valueAndUnitsQuestions[index].index == indexPath.section{
                        self.internalData.valueAndUnitsQuestions[index].units[0].selected = valueAndUnitsCell.getLeftCheckboxChecked()
                        self.internalData.valueAndUnitsQuestions[index].units[1].selected = valueAndUnitsCell.getRightCheckboxChecked()
                    }
                }
            }
            
            for question in internalData.valueAndUnitsQuestions{
                if question.index == indexPath.section{
                    if let currentValue = question.valueAnswer.value{
                        valueAndUnitsCell.setUp(valueText: currentValue, leftLabelText: question.units[0].title, rightLabelText: question.units[1].title, leftCheckboxChecked: question.units[0].selected, rightCheckboxChecked: question.units[1].selected)
                    } else {
                        valueAndUnitsCell.setUp(valueText: "", leftLabelText: question.units[0].title, rightLabelText: question.units[1].title, leftCheckboxChecked: question.units[0].selected, rightCheckboxChecked: question.units[1].selected)
                    }
                    
                }
            }
            return valueAndUnitsCell
        case 2:
            guard let heightTableViewCell:HeightTableViewCell = tableView.dequeueReusableCell(withIdentifier: Constants.Profile.HeightTableViewCellIdentifier, for: indexPath) as? HeightTableViewCell else {
                return defaultCell
            }
            
            heightTableViewCell.valueChanged = {newValue in
                for index in self.internalData.valueAndUnitsQuestions.indices{
                    if self.internalData.valueAndUnitsQuestions[index].index == indexPath.section{
                        self.internalData.valueAndUnitsQuestions[index].valueAnswer.value = newValue
                    }
                }
            }
            
            heightTableViewCell.checkboxChanged = {
                for index in self.internalData.valueAndUnitsQuestions.indices{
                    if self.internalData.valueAndUnitsQuestions[index].index == indexPath.section{
                        self.internalData.valueAndUnitsQuestions[index].units[0].selected = heightTableViewCell.getLeftCheckboxChecked()
                        self.internalData.valueAndUnitsQuestions[index].units[1].selected = heightTableViewCell.getRightCheckboxChecked()
                    }
                }
            }
            
            for question in internalData.valueAndUnitsQuestions{
                if question.index == indexPath.section{
                    if let currentValue = question.valueAnswer.value{
                        heightTableViewCell.setUp(valueText: currentValue, leftCheckboxChecked: question.units[0].selected, rightCheckboxChecked: question.units[1].selected)
                    } else {
                        heightTableViewCell.setUp(valueText: "", leftCheckboxChecked: question.units[0].selected, rightCheckboxChecked: question.units[1].selected)
                    }
                    
                }
            }
            return heightTableViewCell
        case 3:
            guard let valueCell:ValueTableViewCell = tableView.dequeueReusableCell(withIdentifier: Constants.Profile.ValueProfileCellIdentifier, for: indexPath) as? ValueTableViewCell else {
                return defaultCell
            }
            valueCell.valueFieldChanged = {newValue in
                for index in self.internalData.singleValueQuestions.indices{
                    if self.internalData.singleValueQuestions[index].index == indexPath.section{
                        self.internalData.singleValueQuestions[index].valueAnswer.value = newValue
                    }
                }
            }
            for question in internalData.singleValueQuestions{
                if question.index == indexPath.section {
                    if let currentValue = question.valueAnswer.value{
                        valueCell.setUp(valueText: currentValue)
                    } else {
                        valueCell.setUp(valueText: "")
                    }
                }
            }
            return valueCell
        case 4:
            let locationCell = tableView.dequeueReusableCell(withIdentifier: Constants.Profile.BasicProfileCellIdentifier, for: indexPath)
            locationCell.accessoryType = .none
            locationCell.backgroundColor = UIColor.clear
            locationCell.textLabel?.textColor = UIColor(named: .rePerformanceWhite)
            guard let locations = self.locations else {
                return locationCell
            }
            for question in internalData.singleValueQuestions{
                if question.index == indexPath.section{
                    for country in locations.countries{
                        if country.id == question.valueAnswer.value {
                            locationCell.textLabel?.text = country.name
                            return locationCell
                        }
                    }
                    locationCell.textLabel?.text = question.valueAnswer.value
                }
            }
            return locationCell
        case 5:
            let locationCell = tableView.dequeueReusableCell(withIdentifier: Constants.Profile.BasicProfileCellIdentifier, for: indexPath)
            locationCell.accessoryType = .none
            locationCell.backgroundColor = UIColor.clear
            locationCell.textLabel?.textColor = UIColor(named: .rePerformanceWhite)
            guard let locations = self.locations else {
                return locationCell
            }
            var countryID:String? = ""
            for question in internalData.singleValueQuestions{
                if question.index == 4{
                    for country in locations.countries{
                        if country.id == question.valueAnswer.value{
                            countryID = question.valueAnswer.value
                        }
                    }
                }
            }
            for question in internalData.singleValueQuestions{
                if question.index == indexPath.section{
                    for country in locations.countries{
                        if country.id == countryID {
                            for province in country.provinces{
                                if province.id == question.valueAnswer.value {
                                    locationCell.textLabel?.text = province.name
                                    return locationCell
                                }
                            }
                        }
                    }
                    locationCell.textLabel?.text = question.valueAnswer.value
                }
            }
            return locationCell
        case 1, 6:
            let basicProfileCell = tableView.dequeueReusableCell(withIdentifier: Constants.Profile.BasicProfileCellIdentifier, for: indexPath)
            for question in internalData.normalQuestions{
                if question.index == indexPath.section
                {
                    let answer = question.possibleAnswers[indexPath.row]
                    basicProfileCell.textLabel?.text = answer.title
                    if(answer.selected){
                        basicProfileCell.accessoryType = .checkmark
                        basicProfileCell.backgroundColor = UIColor.white
                        basicProfileCell.textLabel?.textColor = UIColor.black
                    } else {
                        basicProfileCell.accessoryType = .none
                        basicProfileCell.backgroundColor = UIColor.clear
                        basicProfileCell.textLabel?.textColor = UIColor(named: .rePerformanceWhite)
                    }
                }
            }
            return basicProfileCell
        default:
            return defaultCell
        }
    }
    
    func tableView(_ tableView: UITableView, heightForHeaderInSection section: Int) -> CGFloat {
        var titleText:String = ""
        switch section{
        case 0, 2:
            for question in internalData.valueAndUnitsQuestions{
                if question.index == section {
                    titleText = question.title
                }
            }
        case 3, 4, 5:
            for question in internalData.singleValueQuestions{
                if question.index == section{
                    titleText = question.title
                }
            }
        case 1, 6:
            for question in internalData.normalQuestions{
                if question.index == section{
                    titleText = question.questionTitle
                }
            }
        default:
            titleText = ""
        }
        return ProfileHeaderView.getHeightForHeaderView(text: titleText)
    }
    
    func tableView(_ tableView: UITableView, viewForHeaderInSection section: Int) -> UIView? {
        var titleText:String = ""
        switch section{
        case 0, 2:
            for question in internalData.valueAndUnitsQuestions{
                if question.index == section {
                    titleText = question.title
                }
            }
        case 3, 4, 5:
            for question in internalData.singleValueQuestions{
                if question.index == section{
                    titleText = question.title
                }
            }
        case 1, 6:
            for question in internalData.normalQuestions{
                if question.index == section{
                    titleText = question.questionTitle
                }
            }
        default:
            titleText = ""
        }
        
        return ProfileHeaderView.getHeaderView(text: titleText)
    }
    
    //If this function is removed, the viewForHeaderInSection will not call for the first section for some reason.
    func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        return "Section Title"
    }
    
    func tableView(_ tableView: UITableView, willSelectRowAt indexPath: IndexPath) -> IndexPath? {
        
        switch indexPath.section {
        case 0, 2:
            return indexPath
        case 3:
            return indexPath
        case 4:
            locationCell?(.Country)
            return indexPath
        case 5:
            locationCell?(.Province)
            return indexPath
        case 1, 6:
            for questionIndex in internalData.normalQuestions.indices{
                if internalData.normalQuestions[questionIndex].index == indexPath.section{
                    //allows for deselection of current selection
                    var deselectCurrentSelection:Bool = false
                    if(internalData.normalQuestions[questionIndex].possibleAnswers[indexPath.row].selected)
                    {
                        deselectCurrentSelection = true
                    }
                    
                    //Update every value to false to reset for current section
                    for index in internalData.normalQuestions[questionIndex].possibleAnswers.indices
                    {
                        internalData.normalQuestions[questionIndex].possibleAnswers[index].selected = false
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
                        internalData.normalQuestions[questionIndex].possibleAnswers[indexPath.row].selected = true
                        tableView.cellForRow(at: indexPath)?.accessoryType = .checkmark
                        tableView.cellForRow(at: indexPath)?.backgroundColor = UIColor.white
                        tableView.cellForRow(at: indexPath)?.textLabel?.textColor = UIColor.black
                    }
                }
            }
            
        default:
            return indexPath
        }
        
        return indexPath
    }


}
