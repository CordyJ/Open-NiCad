//
//  BookAppointmentViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-18.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit
import WebKit
import NVActivityIndicatorView

class BookAppointmentViewController: UIViewController {
    
    var goBack:(()->())?
    
    var webView:WKWebView!
    
    override func loadView() {
        let webConfiguration = WKWebViewConfiguration()
        webView = WKWebView(frame: .zero, configuration: webConfiguration)
        webView.navigationDelegate = self
        view = webView
    }
    
    func loadBookingWebpage(){
        
        NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.ActivityIndicator.activityData)
        if let url = URL(string: Constants.BookAppointment.AppointmentBookingURLString) {
            let request = URLRequest(url: url)
            webView.load(request)
        }
    }

}

extension BookAppointmentViewController:WKNavigationDelegate {
    
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        NVActivityIndicatorPresenter.sharedInstance.stopAnimating()

    }
    
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        handleFailedToLoad()
    }
    
    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        handleFailedToLoad()
    }
    
    func handleFailedToLoad(){
        NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
        let alertController = UIAlertController(title: nil, message: L10n.unableToLoadMessage, preferredStyle: .alert)
        let backAction = UIAlertAction(title: L10n.alertBackTitle, style: .cancel) { (_) in
            self.goBack?()
        }
        let tryAgainAction = UIAlertAction(title: L10n.alertTryAgainTitle, style: .default) { (_) in
            self.loadBookingWebpage()
        }
        alertController.addAction(backAction)
        alertController.addAction(tryAgainAction)
        
        present(alertController, animated: true, completion: nil)
    }
    
}
