//
//  AttributionsViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-13.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import WebKit

class AttributionsViewController: UIViewController {
    
    var webView:WKWebView!
    var willAppear:(()->())?
    
    override func loadView() {
        let webConfiguration = WKWebViewConfiguration()
        webView = WKWebView(frame: .zero, configuration: webConfiguration)
        view = webView
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        willAppear?()
    }
    
    func loadHTMLAttributions(attributions:[String]){
        var htmlString = "<html><body><p>\n"
        for attribution in attributions {
            htmlString = htmlString + "<br>\(attribution)"
        }
        htmlString = htmlString + "\n</p></body></html>"
        
        webView.loadHTMLString(htmlString, baseURL: nil)
    }

}
