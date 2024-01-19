//
//  ValueTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-15.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class ValueTableViewCell: UITableViewCell {
    
    @IBOutlet private var valueTextField:REPCustomTextField?

    let textFieldUpperBounds = 600
    
    var valueFieldChanged: ((String)->())?

    override func awakeFromNib() {
        super.awakeFromNib()
        
        valueTextField?.keyboardType = .numberPad
        valueTextField?.addTarget(self, action: #selector(textFieldDidChange(textField:)), for: .editingChanged)
        valueTextField?.applyProfileWhiteUnderline()
    }
    
    func setUp(valueText:String){
        
        setValueTextFieldText(text: valueText)
        valueTextField?.keyboardType = .numberPad
    }
    
    //MARK: TextField
    
    func setValueTextFieldText(text:String){
        self.valueTextField?.text = text
    }
    
    func getValueTextFieldText() -> String{
        guard let text = self.valueTextField?.text else {
            return ""
        }
        return text
    }
    
    @objc func textFieldDidChange(textField: UITextField){
        if textField == valueTextField{
            if let sanitized:Int = valueTextField?.sanitizeIntegerInput(upperBounds: textFieldUpperBounds) {
                valueTextField?.text = String(sanitized)
                valueFieldChanged?(String(sanitized))
            } else {
                valueTextField?.text = ""
                valueFieldChanged?(String(0))
            }
        }
    }
}
