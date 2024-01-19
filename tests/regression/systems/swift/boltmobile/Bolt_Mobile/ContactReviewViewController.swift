//
//  ContactReviewViewController.swift
//  Bolt Mobile
//
//  Created by Alan Yeung on 2017-09-19.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit
import MapKit

class StoreLocationAnnotation : NSObject, MKAnnotation {
    let storeLocation: StoreLocation
    
    init(storeLocation: StoreLocation) {
        self.storeLocation = storeLocation
    }
    
    var coordinate: CLLocationCoordinate2D {
        return storeLocation.coordinate
    }
}


class ContactReviewViewController: UIViewController, MKMapViewDelegate {
    
    @IBOutlet weak var mapView: MKMapView!
    
    let locationManager = CLLocationManager()
    
    let LocationPinIdentifier = "Location_Pin_Identifier"
    
    var didLoad:(()->())?
    var showStoreLocation:((StoreLocation)->())?
    var didUpdateUserLocation: Bool = false
    
    override func viewDidLoad() {
        super.viewDidLoad()
        didLoad?()
    }
    
    func setUpLocationManager(){
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.requestWhenInUseAuthorization()
    }
    
    func loadStoreLocations(locations:[StoreLocation]) {
        mapView.showsUserLocation = true
        var annotations = [StoreLocationAnnotation]()
        for storeLocation in locations {
            let locationAnnotation = StoreLocationAnnotation(storeLocation: storeLocation)
            annotations.append(locationAnnotation)
        }
        mapView.addAnnotations(annotations as [MKAnnotation])
        zoomMapFitAnnotations(mapView: mapView)
    }
    
    private func zoomMapFitAnnotations(mapView:MKMapView) {
        var zoomRect = MKMapRect.null
        for annotation in mapView.annotations {
            
            let annotationPoint = MKMapPoint(annotation.coordinate)
            
            let pointRect = MKMapRect(x: annotationPoint.x, y: annotationPoint.y, width: 0, height: 0)
            
            if (zoomRect.isNull) {
                zoomRect = pointRect
            } else {
                zoomRect = zoomRect.union(pointRect)
            }
        }
        let customEdgePadding = UIEdgeInsets(top: 50, left: 100, bottom: 50, right: 100)
        mapView.setVisibleMapRect(zoomRect, edgePadding: customEdgePadding, animated: true)
    }

    // MARK: MKMapViewDelegate
    
    func mapView(_ mapView: MKMapView, didUpdate userLocation: MKUserLocation) {
        if didUpdateUserLocation { return }
        didUpdateUserLocation = true
    }
    
    func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
        if annotation is StoreLocationAnnotation {
            let pin = MKAnnotationView(annotation: annotation, reuseIdentifier: LocationPinIdentifier)
            let annotationImage = Asset.Store.pin.image
            pin.image = annotationImage
            pin.centerOffset = CGPoint(x: 0, y: -(annotationImage.size.height/2))
            return pin
        } else {
            return nil
        }
    }
    
    func mapView(_ mapView: MKMapView, didSelect view: MKAnnotationView) {
        if let annotation = view.annotation as? StoreLocationAnnotation {
            showStoreLocation?(annotation.storeLocation)
            self.mapView.deselectAnnotation(annotation, animated: false)
        }
    }
}

extension ContactReviewViewController:CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        if status == .authorizedWhenInUse {
            locationManager.requestLocation()
        } else if status == .denied {
            if let annotations = mapView?.annotations {
                mapView?.showAnnotations(annotations, animated: true)
            }
        }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        //Don't need to do anything if we get the user's location aside from show it on the map, this is done automatically. This method required to be here or the app will crash.
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        //if fail to get location just zoom on the starting location pin
        if let annotations = mapView?.annotations {
            mapView?.showAnnotations(annotations, animated: true)
        }
    }
}

