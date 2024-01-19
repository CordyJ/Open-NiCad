//
//  ExercisesCustomTextField.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-04.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class REPCustomTextField: UITextField {
    
    override func canPerformAction(_ action: Selector, withSender sender: Any?) -> Bool {
        if action == #selector(UIResponderStandardEditActions.paste(_:)) {
            return false
        }
        return super.canPerformAction(action, withSender: sender)
    }
    
    func applyProfileWhiteUnderline(){
        let border = CALayer()
        let borderWidth = CGFloat(Constants.UIConstants.BorderWidth)
        border.borderColor = UIColor.white.cgColor
        let borderFrameWidth = frame.size.width
        border.frame = CGRect(x:0, y:frame.size.height - borderWidth, width:borderFrameWidth, height:frame.size.height)
        
        border.borderWidth = borderWidth
        layer.addSublayer(border)
        layer.masksToBounds = true
    }
    
    func sanitizeIntegerInput(upperBounds: Int) -> Int?
    {
        guard let input = text else{
            return nil
        }
        guard let inputValue: Int = Int(input) else{
            return nil
        }
        let absoluteInput = abs(inputValue)
        
        var output:String = ""
        
        if absoluteInput > upperBounds
        {
            let offset:Int = absoluteInput.digitCount - upperBounds.digitCount == 0 ? 1 : absoluteInput.digitCount - upperBounds.digitCount
            let index = input.index(input.startIndex, offsetBy: absoluteInput.digitCount-offset)
            output = String(input[..<index])
            if output == ""
            {
                return nil
            }
            else
            {
                return Int(output)
            }
        }
        else
        {
            return absoluteInput
        }
    }

}
