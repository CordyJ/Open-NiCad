//
//  ChooseAGymViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-04.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import GoogleMaps

protocol  MapSearchDelegate {
    func didSelectLocation(repPlace:REPPlace)
}

class ChooseAGymViewController: UIViewController {
    
    @IBOutlet private var searchBarView:UIView?
    @IBOutlet fileprivate var mapView:GMSMapView?
    @IBOutlet private var bottomViewConstraint:NSLayoutConstraint?
    @IBOutlet private var bottomView:UIView?
    @IBOutlet private var bottomTitleLabel:UILabel?
    @IBOutlet private var bottomAddressLabel:UILabel?
    
    let locationManager = CLLocationManager()
    var searchController:UISearchController? = nil
    var nearbyGyms:[(repPlace:REPPlace, marker:GMSMarker?)] = []
    var alreadyCalled:Bool = false
    var selectedGym:REPPlace? = nil
    var attributions:[String]? = nil
    
    var didLoad:(()->())?
    var findNearbyGyms:((_ currentLocation:CLLocationCoordinate2D, _ pageToken:String?)->())?
    var selectGym:((REPPlace)->())?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.leftBarButtonItem = UIBarButtonItem(image: Asset.Assets.xIcon.image, style: .plain, target: self, action: #selector(closeButtonTapped(_:)))
        setUpBottomView()
        setUpMap()
        setUpLoactionManager()
        setUpSearchController()
        didLoad?()
//        let text = "Listings by \u{003c}a href=\"http://www.example.com/\"\u{003e}Example Company\u{003c}/a\u{003e}"
//        let data = text.data(using: .nonLossyASCII)
//        let newString = String(data: data!, encoding: .nonLossyASCII)!
//        attributions = [newString]
    }
    
    @IBAction func closeButtonTapped(_ sender:UIButton?){
        self.dismiss(animated: true, completion: nil)
    }
    
    @IBAction func attributionsButtonTapped(_ sender:UIButton?){
        let attributionsVC = StoryboardScene.Leaderboard.attributionsVC.instantiate()
        attributionsVC.willAppear = {
            if let attributions = self.attributions, attributions.count > 0 {
                attributionsVC.loadHTMLAttributions(attributions: attributions)
            }
        }
        navigationController?.pushViewController(attributionsVC, animated: true)
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        if let searchController = searchController, searchController.isActive {
            searchController.dismiss(animated: false, completion: nil)
        }
    }
    
    func loadAttributions(){
        if let attributions = attributions, attributions.count > 0{
            navigationItem.rightBarButtonItem = UIBarButtonItem(title: "Attributions", style: .plain, target: self, action: #selector(attributionsButtonTapped(_:)))
        } else {
            navigationItem.rightBarButtonItem = nil
        }
    }
    
    func setUpBottomView(){
        if let selectedGym = selectedGym {
            bottomTitleLabel?.text = selectedGym.name
            bottomAddressLabel?.text = selectedGym.vicinity
            animateBottomView(up: true)
        } else {
            bottomTitleLabel?.text = ""
            bottomAddressLabel?.text = ""
            animateBottomView(up: false)
        }
    }
    
    func animateBottomView(up:Bool){
        var constant:CGFloat = 0
        if !up {
            if let height = bottomView?.bounds.height {
                constant = -height
            } else {
                constant = -70.0
            }
        }
        UIView.animate(withDuration: 0.5) { 
            self.bottomViewConstraint?.constant = constant
            self.view.layoutIfNeeded()
        }
    }
    
    func setUpMap(){
        mapView?.delegate = self
    }
    
    func searchForNearbyGyms(pageToken:String?) {
        if let userLocation = locationManager.location?.coordinate {
            findNearbyGyms?(userLocation, pageToken)
        }
    }
    
    func showGyms(){
        mapView?.clear()
        var bounds = GMSCoordinateBounds()
        for i in nearbyGyms.indices {
            if let marker = nearbyGyms[i].marker {
                marker.map = mapView
            } else {
                let marker = GMSMarker(position: nearbyGyms[i].repPlace.location)
                marker.title = nearbyGyms[i].repPlace.name
                marker.snippet = nearbyGyms[i].repPlace.vicinity
                marker.icon = GMSMarker.markerImage(with: UIColor(named: .rePerformanceOrange))
                marker.map = mapView
                nearbyGyms[i].marker = marker
            }
            if let position = nearbyGyms[i].marker?.position {
                bounds = bounds.includingCoordinate(position)
            }
            if let userLocation = mapView?.myLocation?.coordinate {
                bounds = bounds.includingCoordinate(userLocation)
            }
        }
        mapView?.animate(with: GMSCameraUpdate.fit(bounds, withPadding: 30.0))
    }
    
    func showPin(repPlace:REPPlace){
        mapView?.clear()
        var bounds = GMSCoordinateBounds()
        let marker = GMSMarker(position: repPlace.location)
        marker.title = repPlace.name
        marker.snippet = repPlace.vicinity
        marker.icon = GMSMarker.markerImage(with: UIColor(named: .rePerformanceOrange))
        marker.map = mapView
        
        bounds = bounds.includingCoordinate(marker.position)
        if let userLocation = mapView?.myLocation?.coordinate {
            bounds = bounds.includingCoordinate(userLocation)
        }
        mapView?.animate(with: GMSCameraUpdate.fit(bounds, withPadding: 30.0))
    }
    
    func setUpLoactionManager(){
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.requestWhenInUseAuthorization()
    }
    
    func setUpSearchController(){
        let mapSearchResultsTableViewController = StoryboardScene.Leaderboard.mapSearchResultsTVC.instantiate()
        mapSearchResultsTableViewController.mapSearchDelegate = self
        let enclosingNav = UINavigationController(rootViewController: mapSearchResultsTableViewController)
        if let currentGymPlaceID = UserDefaults.standard.currentGymPlaceID, currentGymPlaceID != "" {
            mapSearchResultsTableViewController.title = L10n.chooseAGymTitleChange
        } else {
            mapSearchResultsTableViewController.title = L10n.chooseAGymTitleFind
        }
        enclosingNav.navigationBar.setHalfLeaderboardGradientBackground()
        mapSearchResultsTableViewController.mapView = mapView
        
        searchController = UISearchController(searchResultsController: enclosingNav)
        searchController?.searchBar.delegate = mapSearchResultsTableViewController
        
        if let searchBar = searchController?.searchBar{
            searchBarView?.addSubview(searchBar)
            let gradientLayer = CAGradientLayer(frame: searchBar.frame, colors: [UIColor(named: .rePerformanceNavGradientMiddle), UIColor(named: .rePerformanceNavGradientEnd)])
            searchBar.setBackgroundImage(gradientLayer.createGradientImage(), for: .any, barMetrics: .default)
            searchBar.tintColor = UIColor.white
            if let searchTextField:UITextField = searchBar.value(forKey: "searchField") as? UITextField {
                searchTextField.backgroundColor = UIColor.white.withAlphaComponent(Constants.UIConstants.SearchBar.BackgroundAlpha)
                searchTextField.layer.cornerRadius = Constants.UIConstants.SearchBar.CornerRadius
                searchTextField.layer.borderColor = UIColor.white.cgColor
                searchTextField.layer.borderWidth = Constants.UIConstants.SearchBar.BorderWidth
                searchTextField.textColor = UIColor.white
				searchTextField.attributedPlaceholder = NSAttributedString(string: L10n.chooseAGymSearchPlaceholder, attributes: [NSAttributedString.Key.foregroundColor: UIColor.white.withAlphaComponent(Constants.UIConstants.SearchBar.PlaceholderAlpha)])
                if let magnifyingGlassIcon:UIImageView = searchTextField.leftView as? UIImageView {
                    magnifyingGlassIcon.image = magnifyingGlassIcon.image?.withRenderingMode(.alwaysTemplate)
                    magnifyingGlassIcon.tintColor = UIColor.white
                }
                
                if let clearButton:UIButton = searchTextField.value(forKey: "clearButton") as? UIButton {
                    clearButton.setImage(clearButton.imageView?.image?.withRenderingMode(.alwaysTemplate), for: .normal)
                    clearButton.tintColor = UIColor.white
                }
            }
        }
        searchController?.hidesNavigationBarDuringPresentation = false
        searchController?.dimsBackgroundDuringPresentation = false
        searchController?.definesPresentationContext = true
        
    }
    
    @IBAction private func selectButtonTapped(_ sender:UIButton?){
        if let selectedGym = selectedGym {
            selectGym?(selectedGym)
        }
    }
}

extension ChooseAGymViewController:GMSMapViewDelegate {
    func mapView(_ mapView: GMSMapView, didTap marker: GMSMarker) -> Bool {
        for gym in nearbyGyms {
            if gym.marker == marker {
                selectedGym = gym.repPlace
                setUpBottomView()
            }
        }
        
        return false
    }
}

extension ChooseAGymViewController:CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        if status == .authorizedWhenInUse {
            locationManager.requestLocation()
            mapView?.isMyLocationEnabled = true
        } else if status == .denied {
            UIAlertController.showAlert(nil, message: L10n.unableDetermineLocationMessage, inViewController: self)
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        if let mostRecentLocation = locations.last {
            let zoomLevel:Float = 15.0
            
            let camera = GMSCameraPosition.camera(withLatitude: mostRecentLocation.coordinate.latitude, longitude: mostRecentLocation.coordinate.longitude, zoom: zoomLevel)
            mapView?.camera = camera
            
            
            if !alreadyCalled {
                if manager.location != nil {
                    locationManager.stopUpdatingLocation()
                    alreadyCalled = true
                    searchForNearbyGyms(pageToken: nil)
                }
            }
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        UIAlertController.showAlert(nil, message: L10n.unableDetermineLocationMessage, inViewController: self)
    }
}

extension ChooseAGymViewController:MapSearchDelegate {
    
    func didSelectLocation(repPlace: REPPlace) {
        selectedGym = repPlace
        setUpBottomView()
        showPin(repPlace: repPlace)
    }
}
