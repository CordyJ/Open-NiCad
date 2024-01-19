//
//  CouponsViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-21.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit



class CouponsViewController: UIViewController {
    
    @IBOutlet private var tableView:UITableView?
    
    var coupons:Coupons?
    
    var willAppear:(()->())?
    var saveCouponImageAtIndex:((_ index:Int, _ image:UIImage)->())?
    var getCouponAtIndex:((Int)->())?
    
    override func viewDidLoad() {
        tableView?.estimatedRowHeight = 275
        tableView?.rowHeight = UITableView.automaticDimension
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        willAppear?()
    }
    
    func reloadTableView(){
        self.tableView?.reloadData()
    }

}

extension CouponsViewController:UITableViewDataSource {
    func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        guard let coupons = coupons else {
            return 0
        }
        return coupons.allCoupons.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        guard let couponForCell = coupons?.allCoupons[indexPath.row], let couponCell = tableView.dequeueReusableCell(withIdentifier: Constants.Coupons.CouponCellIdentifier, for: indexPath) as? CouponTableViewCell else {
            return UITableViewCell.defaultCell()
        }
        
        couponCell.clearCell()
        
        if let couponImage = couponForCell.couponImage {
            couponCell.configureCell(couponImage: couponImage)
        } else {
            DispatchQueue.global(qos: .background).async {
                if let imageURL = URL(string: couponForCell.couponImageURLString) {
                    var imageData:Data? = nil
                    do{
                        imageData = try Data(contentsOf: imageURL)
                    } catch {
                        DispatchQueue.main.async {
                            couponCell.configureCell(couponImage: nil)
                        }
                    }
                    if let imageData = imageData, let couponImage = UIImage(data: imageData) {
                        DispatchQueue.main.async {
                            self.coupons?.allCoupons[indexPath.row].couponImage = couponImage
                            self.saveCouponImageAtIndex?(indexPath.row, couponImage)
                            couponCell.configureCell(couponImage: couponImage)
                        }
                    } else {
                        DispatchQueue.main.async {
                            couponCell.configureCell(couponImage: nil)
                        }
                    }
                } else {
                    DispatchQueue.main.async {
                        couponCell.configureCell(couponImage: nil)
                    }
                }
            }
        }
        
        couponCell.getCoupon = {
            self.getCouponAtIndex?(indexPath.row)
        }
        
        return couponCell
    }
}

extension CouponsViewController:UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        getCouponAtIndex?(indexPath.row)
    }
}
