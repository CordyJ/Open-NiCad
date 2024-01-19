//
//  UITextField+Designable.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-21.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

@IBDesignable class LightBlueBorderTextField:UITextField {
    
    override func placeholderRect(forBounds bounds: CGRect) -> CGRect {
        return bounds.insetBy(dx: 20, dy: 0)
    }
    
    override func textRect(forBounds bounds: CGRect) -> CGRect {
        return bounds.insetBy(dx: 20, dy: 0)
    }
    
    override func editingRect(forBounds bounds: CGRect) -> CGRect {
        return bounds.insetBy(dx: 20, dy: 0)
    }
    
    func commonInit() {
        borderStyle = .none
        textColor = UIColor(named: .boltMobileBlueLabel)
        layer.borderColor = UIColor(named: .boltMobileLightBlueLabel).cgColor
        layer.borderWidth = 1.0
    }
    
    override init(frame: CGRect){
        super.init(frame: frame)
        commonInit()
    }
    
    required init?(coder aDecoder:NSCoder) {
        super.init(coder: aDecoder)
        commonInit()
    }
    
    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
        commonInit()
    }
}

@IBDesignable class VerificationCodeTextField:UITextField {
    override func placeholderRect(forBounds bounds: CGRect) -> CGRect {
        return bounds.insetBy(dx: 20, dy: 0)
    }
    
    override func textRect(forBounds bounds: CGRect) -> CGRect {
        return bounds.insetBy(dx: 20, dy: 0)
    }
    
    override func editingRect(forBounds bounds: CGRect) -> CGRect {
        return bounds.insetBy(dx: 20, dy: 0)
    }
    
    override func canPerformAction(_ action: Selector, withSender sender: Any?) -> Bool {
        //Do not allow them to paste random characters into text field
        if action == #selector(UIResponderStandardEditActions.paste(_:)) {
            return false
        }
        return super.canPerformAction(action, withSender: sender)
    }
    
    func commonInit() {
        borderStyle = .none
        textColor = UIColor(named: .boltMobileBlueLabel)
        layer.borderColor = UIColor(named: .boltMobileLightBlueLabel).cgColor
        layer.borderWidth = 1.0
        
        //Only allow for numbers to be entered
        keyboardType = .numberPad
    }
    
    override init(frame: CGRect){
        super.init(frame: frame)
        commonInit()
    }
    
    required init?(coder aDecoder:NSCoder) {
        super.init(coder: aDecoder)
        commonInit()
    }
    
    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
        commonInit()
    }

}
