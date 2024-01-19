//
//  UIButton+Designable.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-15.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

@IBDesignable class BoltMobileGradientButton:UIButton {
    
    func commonInit() {
        setTitleColor(UIColor.white, for: .normal)
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0.0, height: 2.0)
        layer.shadowRadius = 3.0
        layer.shadowOpacity = 0.5
        layer.masksToBounds = false
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
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        if (backgroundImage(for: .normal) == nil)
        {
            let colors = [UIColor(named: .boltMobileGradientDark), UIColor(named: .boltMobileGradientLight)]
            let gradientLayer = CAGradientLayer(frame: frame, colors: colors, gradientDirection: .horizontal)
            let gradientImage = gradientLayer.createGradientImage()
            setBackgroundImage(gradientImage, for: .normal)
            setBackgroundImage(gradientImage, for: .highlighted)
        }
    }
}

@IBDesignable class BoltMobileGradient15BoldButton: BoltMobileGradientButton {

    override func commonInit() {
        super.commonInit()
        titleLabel?.font = UIFont.boldSystemFont(ofSize: 15)
    }
    
    required init?(coder aDecoder:NSCoder) {
        super.init(coder: aDecoder)
    }
}

@IBDesignable class BoltMobileGradient32BoldButton: BoltMobileGradientButton {
    
    override func commonInit() {
        super.commonInit()
        titleLabel?.font = UIFont.boldSystemFont(ofSize: 32)
    }
    
    required init?(coder aDecoder:NSCoder) {
        super.init(coder: aDecoder)
    }
}



@IBDesignable class HomeScreenButton:UIButton {
    func commonInit() {
        setTitleColor(UIColor(named: .boltMobileHomeButtonText), for: .normal)
        titleLabel?.font = UIFont.boldSystemFont(ofSize: 15)
        titleLabel?.textAlignment = .center
        titleLabel?.lineBreakMode = .byWordWrapping
        backgroundColor = UIColor(named: .boltMobileHomeBackgroundColour)
        
        layer.shadowColor = UIColor(named: .boltMobileHomeShadowColour).cgColor
        layer.shadowOffset = CGSize(width: 0.0, height: 6.0)
        layer.shadowRadius = 10.0
        layer.shadowOpacity = 0.13
        layer.masksToBounds = false
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
    
    override func layoutSubviews() {
        super.layoutSubviews()

        if (backgroundImage(for: .normal) == nil)
        {
            let colors = [UIColor(named: .boltMobileHomeGradientDark), UIColor(named: .boltMobileHomeGradientLight)]
            let gradientLayer = CAGradientLayer(frame: frame, colors: colors, gradientDirection: .diagonal)
            let gradientImage = gradientLayer.createGradientImage()
            setBackgroundImage(gradientImage, for: .normal)
            setBackgroundImage(gradientImage, for: .highlighted)
        }
        alignImageAndTitleVertically()
    }
}

@IBDesignable class BorderGradientButton:UIButton {

    
    func commonInit() {
        setTitleColor(UIColor(named: .boltMobileBlueLabel), for: .normal)
        titleLabel?.font = UIFont.boldSystemFont(ofSize: 15)
        
        layer.cornerRadius = 5.0
        
        layer.masksToBounds = true
        
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
    
    override func layoutSubviews() {
        super.layoutSubviews()
        let gradient = CAGradientLayer()
        gradient.frame =  CGRect(origin: CGPoint.zero, size: frame.size)
        gradient.colors = [UIColor(named: .boltMobileGradientDark).cgColor, UIColor(named: .boltMobileGradientLight).cgColor]
        gradient.startPoint = CGPoint(x: 0, y: 0)
        gradient.endPoint = CGPoint(x: 1, y: 0)
        
        let shape = CAShapeLayer()
        shape.lineWidth = 4.0
        shape.path = UIBezierPath(rect: bounds).cgPath
        shape.strokeColor = UIColor.black.cgColor
        shape.fillColor = UIColor.clear.cgColor
        gradient.mask = shape
        
        layer.addSublayer(gradient)
    }
}

@IBDesignable class CouponButton:UIButton {
    
    
    func commonInit() {
        setTitleColor(UIColor(named: .boltMobileBlueLabel), for: .normal)
        titleLabel?.font = UIFont.systemFont(ofSize: 15)
        
        layer.borderColor = UIColor(named: .boltMobileBlueLabel).cgColor
        layer.borderWidth = 2.0
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

