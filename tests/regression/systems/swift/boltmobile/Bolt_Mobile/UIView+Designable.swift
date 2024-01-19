//
//  UIView+Designable.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-20.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

@IBDesignable class HomescreenBackgroundView:UIView{
    func commonInit(){
        backgroundColor = UIColor(named: .boltMobileHomeBackgroundColour)
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

@IBDesignable class CouponBackgroundView:UIView{
    func commonInit(){
        backgroundColor = UIColor(named: .boltMobileHomeBackgroundColour)
        
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0.0, height: 2.0)
        layer.shadowRadius = 10.0
        layer.shadowOpacity = 0.3
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
}
        
@IBDesignable class RedeemBackgroundView:UIView{
    func commonInit(){
        backgroundColor = UIColor(named: .boltMobileDarkBlue)
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
