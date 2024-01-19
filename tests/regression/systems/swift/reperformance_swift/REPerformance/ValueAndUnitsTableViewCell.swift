//
//  ValueAndUnitsTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-15.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import M13Checkbox

class ValueAndUnitsTableViewCell: ValueTableViewCell {
    
    @IBOutlet private var leftLabel: UILabel?
    @IBOutlet private var rightLabel:UILabel?
    @IBOutlet private var leftCheckbox: M13Checkbox?
    @IBOutlet private var rightCheckbox: M13Checkbox?
    
    var checkboxChanged: (()->())?
    
    override func awakeFromNib() {
        super.awakeFromNib()
        leftLabel?.textColor = UIColor.white
        rightLabel?.textColor = UIColor.white
        
		leftCheckbox?.addTarget(self, action: #selector(checkboxValueChanged(checkbox:)), for: UIControl.Event.valueChanged)
		rightCheckbox?.addTarget(self, action: #selector(checkboxValueChanged(checkbox:)), for: UIControl.Event.valueChanged)

    }
    
    func setUp(valueText:String, leftLabelText:String, rightLabelText:String, leftCheckboxChecked:Bool, rightCheckboxChecked:Bool){
        super.setUp(valueText: valueText)
        
        setLeftTextLabelWithText(leftLabelText)
        setRightTextLabelWithText(rightLabelText)
        setLeftCheckBoxChecked(leftCheckboxChecked)
        setRightCheckBoxChecked(rightCheckboxChecked)
    }
    

    
    //MARK: Checkbox
    
    func getLeftCheckboxChecked() -> Bool{
        guard let leftCheckbox = leftCheckbox else {
            return false
        }
        return checkState(checkbox: leftCheckbox)
    }
    
    func getRightCheckboxChecked() -> Bool {
        guard let rightCheckbox = rightCheckbox else {
            return false
        }
        return checkState(checkbox: rightCheckbox)
    }
    
    func checkState(checkbox: M13Checkbox) -> Bool{
        return checkbox._IBCheckState == "Checked"
    }
    
    func setLeftCheckBoxChecked(_ checked:Bool){
        guard let leftCheckbox = leftCheckbox else {
            return
        }
        setCheckboxValueWith(checkbox: leftCheckbox, checked: checked)
    }
    
    func setRightCheckBoxChecked(_ checked:Bool){
        guard let rightCheckbox = rightCheckbox else {
            return
        }
        setCheckboxValueWith(checkbox: rightCheckbox, checked: checked)
    }
    
    @objc func checkboxValueChanged(checkbox: M13Checkbox)
    {
        if checkbox == leftCheckbox {
            if getLeftCheckboxChecked() {
                setRightCheckBoxChecked(false)
            }else{
                setLeftCheckBoxChecked(true)
            }
        } else if checkbox == rightCheckbox {
            if(getRightCheckboxChecked()){
                setLeftCheckBoxChecked(false)
            } else {
                setRightCheckBoxChecked(true)
            }
        } else {
            setRightCheckBoxChecked(false)
            setLeftCheckBoxChecked(false)
        }
        checkboxChanged?()
    }
    
    private func setCheckboxValueWith(checkbox:M13Checkbox, checked:Bool)
    {
        if(checked){
            checkbox.setCheckState(.checked, animated: true)
        }
        else {
            checkbox.setCheckState(.unchecked, animated: true)
        }
    }
    
    //MARK: Labels
    func setLeftTextLabelWithText(_ text:String){
        self.leftLabel?.text = text
    }
    
    func setRightTextLabelWithText(_ text:String){
        self.rightLabel?.text = text
    }

}
