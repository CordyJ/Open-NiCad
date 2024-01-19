//
//  UILabel+Designable.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-18.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

@IBDesignable class WelcomeScreenLabel:UILabel{
    func commonInit(){
        text = L10n.welcomeText
        textColor = UIColor.white
        font = UIFont.boldSystemFont(ofSize: 22)
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOffset = CGSize(width: 0.0, height: 2.0)
        layer.shadowRadius = 3.0
        layer.shadowOpacity = 0.5
        layer.masksToBounds = false
        layer.shouldRasterize = true
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

@IBDesignable class Blue15Label:UILabel{
    func commonInit(){
        textColor = UIColor(named: .boltMobileBlueLabel)
        font = UIFont.systemFont(ofSize: 15)
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

@IBDesignable class Blue17Label:UILabel{
    func commonInit(){
        textColor = UIColor(named: .boltMobileBlueLabel)
        font = UIFont.systemFont(ofSize: 17)
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

@IBDesignable class BoldBlue17Label:UILabel{
    func commonInit(){
        textColor = UIColor(named: .boltMobileBlueLabel)
        font = UIFont.boldSystemFont(ofSize: 17)
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

@IBDesignable class BoldBlue22Label:UILabel {
    func commonInit(){
        textColor = UIColor(named: .boltMobileBlueLabel)
        font = UIFont.boldSystemFont(ofSize: 22)
        
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

@IBDesignable class BoldLightBlue15Label:UILabel {
    func commonInit(){
        textColor = UIColor(named: .boltMobileLightBlueLabel)
        font = UIFont.boldSystemFont(ofSize: 15)
        
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

@IBDesignable class BoldBlue15Label:UILabel{
    func commonInit(){
        textColor = UIColor(named: .boltMobileBlueLabel)
        font = UIFont.boldSystemFont(ofSize: 15)
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

@IBDesignable class BoldBlue30Label:UILabel{
    func commonInit(){
        textColor = UIColor(named: .boltMobileBlueLabel)
        font = UIFont.boldSystemFont(ofSize: 30)
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


@IBDesignable class BoldBlue40Label:UILabel{
    func commonInit(){
        textColor = UIColor(named: .boltMobileBlueLabel)
        font = UIFont.boldSystemFont(ofSize: 40)
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

@IBDesignable class BoldLightBlue50Label:UILabel{
    func commonInit(){
        textColor = UIColor(named: .boltMobileLightBlueLabel)
        font = UIFont.boldSystemFont(ofSize: 50)
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

@IBDesignable class WhiteLabel:UILabel {
    func commonInit(){
        textColor = UIColor.white
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
