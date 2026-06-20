# Delivery Center Gold Answers

## Query 1

Among hub cities with at least 1,000 finished FOOD orders with paid payments and completed deliveries in both February and March, which city had the largest increase in average paid basket from February to March? Return the city, February order count, February average paid basket, March order count, March average paid basket, and the change rounded to 2 decimals.

hub_city,feb_orders,feb_avg_paid_basket,mar_orders,mar_avg_paid_basket,avg_paid_change
PORTO ALEGRE,7246,71.59,8134,79.61,8.01

## Query 2

Which store segment and channel type combination had a higher cancellation rate in April than January, while its average cycle time for finished orders decreased over the same months? Consider only combinations with at least 500 orders in both months. Return segment, channel type, January cancellation rate, April cancellation rate, cancellation-rate change, January average cycle time, April average cycle time, and cycle-time change, rounded to 2 decimals.

store_segment,channel_type,jan_cancel_rate,apr_cancel_rate,cancel_rate_change,jan_avg_cycle_time,apr_avg_cycle_time,cycle_time_change
FOOD,OWN CHANNEL,4.88,6.33,1.45,160.00,93.57,-66.43

## Query 3

Among stores with at least 150 finished orders in every month from January through April, which five stores had the largest absolute paid-minus-order gap per paid-backed finished order? For the reconciliation totals, include only finished orders that have paid payment records. Return store token, store name, hub name, paid-backed finished order count, total order amount, total paid amount, and paid-minus-order gap per order rounded to 2 decimals.

store_ref,store_name,hub_name,finished_orders,total_order_amount,total_paid_amount,paid_minus_order_per_order
STORECARD-000676,IUMPICA,PAGODE SHOPPING,12276,1637526.52,1783536.82,11.89
STORECARD-000496,IUMPICA,SQL SHOPPING,4938,613837.00,672432.60,11.87
STORECARD-000417,IUMPICA,PURPLE SHOPPING,3555,464615.20,506753.11,11.85
STORECARD-000658,IUMPICA,SUBWAY SHOPPING,7358,1013773.94,1100798.70,11.83
STORECARD-000416,IUMPICA,WOLF SHOPPING,5179,706821.93,768047.48,11.82

## Query 4

Which ten drivers with at least 50 completed deliveries in each month had an OWN CHANNEL delivery share that increased every month from January through April? Return driver token, modal, type, January share, February share, March share, April share, and total completed deliveries. Sort by total completed deliveries descending.

driver_ref,driver_modal,driver_type,jan_own_channel_share,feb_own_channel_share,mar_own_channel_share,apr_own_channel_share,total_completed_deliveries
DRIVER-CARD-17749,MOTOBOY,FREELANCE,2.39,2.59,11.44,14.49,887
DRIVER-CARD-00794,BIKER,FREELANCE,3.19,4.57,6.14,9.35,735
DRIVER-CARD-10927,MOTOBOY,FREELANCE,4.11,5.15,15.73,18.75,674
DRIVER-CARD-32130,MOTOBOY,LOGISTIC OPERATOR,5.00,9.94,13.58,14.63,669
DRIVER-CARD-01203,BIKER,FREELANCE,2.52,2.58,12.74,15.00,646
DRIVER-CARD-24584,MOTOBOY,FREELANCE,2.99,5.06,20.45,30.95,640
DRIVER-CARD-31999,MOTOBOY,FREELANCE,10.88,11.64,27.63,32.26,614
DRIVER-CARD-18715,MOTOBOY,FREELANCE,2.63,8.33,17.37,18.71,602
DRIVER-CARD-25592,MOTOBOY,FREELANCE,7.41,10.38,15.96,23.33,601
DRIVER-CARD-14059,BIKER,FREELANCE,5.41,6.29,7.82,13.93,592

## Query 5

Among payment methods with at least 500 paid finished orders in both January and April, which three had the largest drop in late-night order share from January to April? Treat late night as order hours 22 through 5. Return payment method, January paid-order count, January late-night share, April paid-order count, April late-night share, and percentage-point change rounded to 2 decimals.

payment_method,jan_paid_orders,jan_late_night_share,apr_paid_orders,apr_late_night_share,late_night_share_change
CREDIT,1171,35.08,1219,23.05,-12.02
VOUCHER,8170,42.39,13189,32.42,-9.98
STORE_DIRECT_PAYMENT,825,16.85,1603,7.98,-8.87

## Query 6

For hub cities with at least 1,000 completed deliveries in both FOOD and GOOD segments, which cities have FOOD deliveries that are farther on average but earn less paid amount per kilometer than GOOD deliveries? Return city, FOOD count, GOOD count, FOOD average distance, GOOD average distance, FOOD paid amount per kilometer, and GOOD paid amount per kilometer rounded to 2 decimals. Row order is not important.

hub_city,food_completed_deliveries,good_completed_deliveries,food_avg_distance_meters,good_avg_distance_meters,food_paid_per_km,good_paid_per_km
CURITIBA,26644,3021,15634.42,10630.41,3.44,20.73
SÃO PAULO,137083,27754,11018.07,8427.47,9.36,27.26

## Query 7

Which sales channel had the GOOD-segment share of paid order amount at least double from January to April, considering finished paid orders with completed deliveries and at least 200 such orders in each month? Return channel name, channel type, January order count, January GOOD paid share, April order count, April GOOD paid share, and percentage-point change rounded to 2 decimals.

channel_name,channel_type,jan_orders,jan_good_paid_share,apr_orders,apr_good_paid_share,good_paid_share_change
FOOD PLACE,MARKETPLACE,60337,0.44,79226,1.36,0.91

## Query 8

For each hub state with at least 500 March orders from both zero-plan stores and paid-plan stores, compare the March cancellation rate of zero-plan stores against paid-plan stores. Return state, zero-plan order count, zero-plan cancellation rate, paid-plan order count, paid-plan cancellation rate, and zero-minus-paid cancellation penalty rounded to 2 decimals. Row order is not important.

hub_state,zero_plan_orders,zero_plan_cancel_rate,paid_plan_orders,paid_plan_cancel_rate,cancellation_penalty
PR,711,9.70,10309,4.98,4.73
RS,3270,4.22,6666,5.60,-1.38
SP,21114,1.55,30598,4.35,-2.80
RJ,24222,2.91,15333,10.00,-7.09

