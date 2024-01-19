//
//  UINavigationBar+REPerformance.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-04.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

extension UINavigationBar {
    
    func setHalfLeaderboardGradientBackground(){
        setGradientBackground(colors: [UIColor(named: .rePerformanceNavGradientStart), UIColor(named: .rePerformanceNavGradientMiddle)])
    }
    
    func setFullLeaderboardGradientBackground(){
        setGradientBackground(colors: [UIColor(named: .rePerformanceNavGradientStart), UIColor(named: .rePerformanceNavGradientEnd)])
    }
    
    private func setGradientBackground(colors: [UIColor]) {
        
        var updatedFrame = bounds
        updatedFrame.size.height += 20
        updatedFrame.size.width = UIScreen.main.bounds.width
        let gradientLayer = CAGradientLayer(frame: updatedFrame, colors: colors)
        
        setBackgroundImage(gradientLayer.createGradientImage(), for: UIBarMetrics.default)
        
        isTranslucent = false
    }
    
    func removeHairline() {
        shadowImage = UIImage.oneByOneImage(with: UIColor.clear)
    }
    
    func addHairline() {
        shadowImage = nil
    }
}
