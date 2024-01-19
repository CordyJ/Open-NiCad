//
//  NVActivityIndicatorView+Push.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-08.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import NVActivityIndicatorView

extension NVActivityIndicatorView{
    
    class func centredActivityIndicator(in view: UIView) -> NVActivityIndicatorView {
        let xPos:CGFloat = (view.frame.width/2)-((view.frame.width/4)/2)
        let yPos:CGFloat = (view.frame.height/2)-((view.frame.height/4)/2)
        let activityIndicatorFrame:CGRect = CGRect(x: xPos, y: yPos, width: view.frame.width/4, height: view.frame.height/4)
        let activityIndicatorView = NVActivityIndicatorView(frame: activityIndicatorFrame, type: .ballPulse, color: .white, padding: 0)
        return activityIndicatorView
    }
}
