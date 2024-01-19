//
//  WeightTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-17.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import M13Checkbox

class HeightTableViewCell: UITableViewCell {

    @IBOutlet private var checkboxFeetInchesLabel: UILabel?
    @IBOutlet private var checkboxCmLabel:UILabel?
    @IBOutlet private var leftCheckbox: M13Checkbox?
    @IBOutlet private var rightCheckbox: M13Checkbox?
    
    @IBOutlet private var ftLabel:UILabel?
    @IBOutlet private var inLabel:UILabel?
    @IBOutlet private var cmLabel:UILabel?
    
    @IBOutlet private var feetInchesView:UIView?
    @IBOutlet private var cmView:UIView?
    
    @IBOutlet private var ftTextField:REPCustomTextField?
    @IBOutlet private var inTextField:REPCustomTextField?
    @IBOutlet private var cmTextField:REPCustomTextField?
    
    var checkboxChanged: (()->())?
    var valueChanged:((String)->())?
    
    var feet:Int = 0
    var inches:Int = 0
    
    let ftTextFieldUpperBounds = 9
    let inTextFieldUpperBounds = 11
    let cmTextFieldUpperBounds = 303
    
    override func awakeFromNib() {
        super.awakeFromNib()
        checkboxFeetInchesLabel?.textColor = UIColor.white
        checkboxCmLabel?.textColor = UIColor.white
        
        ftLabel?.textColor = UIColor(named: .rePerformanceOrange)
        inLabel?.textColor = UIColor(named: .rePerformanceOrange)
        cmLabel?.textColor = UIColor(named: .rePerformanceOrange)
        
		leftCheckbox?.addTarget(self, action: #selector(checkboxValueChanged(checkbox:)), for: UIControl.Event.valueChanged)
		rightCheckbox?.addTarget(self, action: #selector(checkboxValueChanged(checkbox:)), for: UIControl.Event.valueChanged)
        
        ftTextField?.keyboardType = .numberPad
        ftTextField?.addTarget(self, action: #selector(textFieldDidChange(textField:)), for: .editingChanged)
        ftTextField?.applyProfileWhiteUnderline()
        
        inTextField?.keyboardType = .numberPad
        inTextField?.addTarget(self, action: #selector(textFieldDidChange(textField:)), for: .editingChanged)
        inTextField?.applyProfileWhiteUnderline()
        
        cmTextField?.keyboardType = .numberPad
        cmTextField?.addTarget(self, action: #selector(textFieldDidChange(textField:)), for: .editingChanged)
        cmTextField?.applyProfileWhiteUnderline()
    }
    
    func setUp(valueText:String, leftCheckboxChecked:Bool, rightCheckboxChecked:Bool){
        if leftCheckboxChecked && valueText != "" {
            if valueText != "" {
                if let valueInt = Int(valueText) {
                    feet = valueInt/12
                    inches = valueInt - (feet*12)
                    ftTextField?.text = String(feet)
                    inTextField?.text = String(inches)
                    setLeftCheckBoxChecked(leftCheckboxChecked)
                    cmView?.isHidden = true
                    feetInchesView?.isHidden = false
                }
            }
        } else if rightCheckboxChecked && valueText != "" {
            cmTextField?.text = valueText
            setRightCheckBoxChecked(rightCheckboxChecked)
            feetInchesView?.isHidden = true
            cmView?.isHidden = false
        } else {
            feetInchesView?.isHidden = false
            cmView?.isHidden = true
        }
        if !self.getLeftCheckboxChecked() && !self.getRightCheckboxChecked() {
            self.setLeftCheckBoxChecked(true)
            checkboxChanged?()
        }
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
                feetInchesView?.isHidden = false
                cmView?.isHidden = true
                setZero()
            }else{
                setLeftCheckBoxChecked(true)
            }
        } else if checkbox == rightCheckbox {
            if(getRightCheckboxChecked()){
                setLeftCheckBoxChecked(false)
                feetInchesView?.isHidden = true
                cmView?.isHidden = false
                setZero()
            } else {
                setRightCheckBoxChecked(true)
            }
        } else {
            setRightCheckBoxChecked(false)
            setLeftCheckBoxChecked(false)
            feetInchesView?.isHidden = true
            cmView?.isHidden = true
            setZero()
        }
        checkboxChanged?()
    }
    
    private func setZero(){
        valueChanged?(String(0))
        ftTextField?.text = "0"
        inTextField?.text = "0"
        cmTextField?.text = "0"
        feet = 0
        inches = 0
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
    
    
    @objc func textFieldDidChange(textField: UITextField){
        
        if textField == ftTextField {
            if let sanitized:Int = ftTextField?.sanitizeIntegerInput(upperBounds: ftTextFieldUpperBounds) {
                ftTextField?.text = String(sanitized)
                feet = sanitized
                valueChanged?(String((feet*12)+inches))
            } else {
                ftTextField?.text = ""
                feet = 0
                valueChanged?(String(0))
            }
            
        } else if textField == inTextField {
            if let sanitized:Int = inTextField?.sanitizeIntegerInput(upperBounds: inTextFieldUpperBounds) {
                inTextField?.text = String(sanitized)
                inches = sanitized
                valueChanged?(String((feet*12)+inches))
            } else {
                inTextField?.text = ""
                inches = 0
                valueChanged?(String(0))
            }
            
        } else if textField == cmTextField {
            if let sanitized:Int = cmTextField?.sanitizeIntegerInput(upperBounds: cmTextFieldUpperBounds){
                cmTextField?.text = String(sanitized)
                valueChanged?(String(sanitized))
            } else {
                cmTextField?.text = ""
                valueChanged?(String(0))
            }
        }
    }
}
