//
//  Buttons.swift
//
//  Created by Alan Yeung on 2017-04-05.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit


extension UIView {
	
	@IBInspectable var borderWidth: CGFloat {
		get {
			return layer.borderWidth
		}
		set {
			layer.borderWidth = newValue
		}
	}
	
	@IBInspectable var borderColor: UIColor {
		get {
			return layer.borderColor != nil ? UIColor.init(cgColor: layer.borderColor!) : UIColor.black
		}
		set {
			layer.borderColor = newValue.cgColor
		}
	}
	
	@IBInspectable var cornerRadius: CGFloat {
		get {
			return layer.cornerRadius
		}
		set {
			layer.cornerRadius = newValue
		}
	}
}


extension UIButton {
	@IBInspectable var textColor: UIColor {
		get {
			return titleColor(for: .normal) ?? UIColor.clear
		}
		set {
			setTitleColor(newValue, for: .normal)
		}
	}
}

extension UIButton {
    
    public func setUpWhiteLogoutButton(){
        textColor = UIColor.white
        layer.cornerRadius = Constants.UIConstants.LogoutButtonCornerRadius
        layer.borderColor = UIColor.white.cgColor
        layer.borderWidth = Constants.UIConstants.BorderWidth
        layer.masksToBounds = true
        backgroundColor = UIColor.clear
    }
    
    public func setUpOrangeREPerformanceButton(){
        textColor = UIColor.white
        layer.cornerRadius = Constants.UIConstants.CornerRadius
        layer.masksToBounds = true
        backgroundColor = UIColor.init(named: .rePerformanceOrange)
        setEnabled(enabled: isEnabled)
    }
    
    public func setEnabled(enabled: Bool)
    {
        isEnabled = enabled
        if isEnabled{
            alpha = 1.0
        }
        else
        {
            alpha = 0.5
        }
    }
    
    public func setUpWhiteREPerformanceButton(){
        textColor = UIColor.white
        layer.cornerRadius = Constants.UIConstants.CornerRadius
        layer.masksToBounds = true
        backgroundColor = UIColor.clear
        borderWidth = Constants.UIConstants.BorderWidth
        borderColor = UIColor.white
    }
    
    public func setUpBlueButton(){
        textColor = UIColor(named: .rePerformanceBlueText)
        borderWidth = Constants.UIConstants.BorderWidth
        borderColor = UIColor(named: .rePerformanceBlueText)
        layer.cornerRadius = Constants.UIConstants.CornerRadius
        layer.masksToBounds = true
    }
    
    public func setUpShareOnInstagramButton(){
        textColor = UIColor(named: .rePerformanceBlueText)
        layer.cornerRadius = Constants.UIConstants.CornerRadius
        layer.masksToBounds = true
        backgroundColor = UIColor.white
        setEnabled(enabled: isEnabled)
        imageView?.contentMode = .scaleAspectFit
        semanticContentAttribute = .forceRightToLeft
    }
}

extension UIImage {
	
	static func imageFromColor(color: UIColor) -> UIImage? {
		let rect = CGRect(x: 0, y: 0, width: 1, height: 1)
		
		UIGraphicsBeginImageContext(rect.size)
		
		let context = UIGraphicsGetCurrentContext()
		context?.setFillColor(color.cgColor)
		context?.fill(rect)
		
		let image = UIGraphicsGetImageFromCurrentImageContext()
		
		return image
	}
}


class BorderButton: UIButton {
	
	func commonInit() {
		borderWidth = 2
		borderColor = UIColor.clear
		textColor = UIColor.black
	}
	
	override init(frame: CGRect) {
		super.init(frame: frame)
		commonInit()
	}
	
	required init?(coder aDecoder: NSCoder) {
		super.init(coder: aDecoder)
		commonInit()
	}
    
    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
        commonInit()
    }
}


class RoundButton: UIButton {
	func commonInit() {
		borderWidth = 0
		cornerRadius = 5
		textColor = UIColor.black
	}
	
	override init(frame: CGRect) {
		super.init(frame: frame)
		commonInit()
	}
	
	required init?(coder aDecoder: NSCoder) {
		super.init(coder: aDecoder)
		commonInit()
	}
    
    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
        commonInit()
    }
}
